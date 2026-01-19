"""
Script to deploy a consolidated CloudFormation template for a website framework.

This script automates the deployment of the cfn-website-framework.yaml template.
It uses parameters for ACM certificates, domain name, project prefix, and bucket lifecycle configurations.

Usage:
    python deploy.py --domain <DOMAIN_NAME> --prefix <PROJECT_PREFIX> [--account <AWS_PROFILE>] [--region <AWS_REGION>]

Example (local with profile):
    python deploy.py --account myprofile --region us-east-1 --domain example.com --prefix myproject

Example (CI with OIDC credentials):
    python deploy.py --region us-east-1 --domain example.com --prefix myproject
"""

import time
import argparse
import logging
import boto3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_template(client, template_body):
    """
    Validate the CloudFormation template.

    Args:
        client: boto3 CloudFormation client.
        template_body: The CloudFormation template body as a string.

    Returns:
        dict: Validation response from CloudFormation.
    """
    logger.info("Validating template... %s", template_body)
    response = client.validate_template(TemplateBody=template_body)
    logger.info("Template validation response: %s", response)
    return response


def deploy_stack(client, stack_name, template_body, parameters):
    """
    Deploy or update a CloudFormation stack.

    Args:
        client: boto3 CloudFormation client.
        stack_name: Name of the stack to deploy or update.
        template_body: The CloudFormation template body as a string.
        parameters: List of parameters to pass to the stack.
    """
    try:
        logger.info("Checking if stack %s exists...", stack_name)
        client.describe_stacks(StackName=stack_name)
        logger.info("Stack %s exists. Updating...", stack_name)
        try:
            client.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
            )
            waiter = client.get_waiter("stack_update_complete")
            waiter.wait(StackName=stack_name)
            logger.info("Stack %s updated successfully.", stack_name)
        except client.exceptions.ClientError as e:
            if "No updates are to be performed" in str(e):
                logger.info("No updates detected for stack %s.", stack_name)
            else:
                raise
    except client.exceptions.ClientError as e:
        if "does not exist" in str(e):
            logger.info("Stack %s does not exist. Creating...", stack_name)
            client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=parameters,
                Capabilities=["CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
            )
            waiter = client.get_waiter("stack_create_complete")
            waiter.wait(StackName=stack_name)
            logger.info("Stack %s created successfully.", stack_name)
        else:
            raise


def get_existing_certificate(domain, acm_client):
    """
    Check for an existing valid ACM certificate for the domain.

    Args:
        domain: The domain name.
        acm_client: Boto3 ACM client.

    Returns:
        str: ACM Certificate ARN if found and valid, None otherwise.
    """
    response = acm_client.list_certificates(
        CertificateStatuses=["ISSUED", "PENDING_VALIDATION"]
    )

    for cert in response.get("CertificateSummaryList", []):
        if cert["DomainName"] == domain:
            cert_arn = cert["CertificateArn"]
            # Verify the certificate includes www subdomain
            cert_details = acm_client.describe_certificate(CertificateArn=cert_arn)
            sans = cert_details["Certificate"].get("SubjectAlternativeNames", [])
            if f"www.{domain}" in sans:
                status = cert_details["Certificate"]["Status"]
                if status == "ISSUED":
                    logger.info("Found existing valid certificate: %s", cert_arn)
                    return cert_arn
                logger.info(
                    "Found existing certificate (status: %s): %s", status, cert_arn
                )
                return cert_arn
    return None


def request_acm_certificate(domain, zone_id, acm_client, route53_client):
    """
    Request an ACM certificate for the domain and validate it using Route 53.
    First checks for an existing valid certificate.

    Args:
        domain: The domain name.
        zone_id: Hosted zone ID for the domain.
        acm_client: Boto3 ACM client.
        route53_client: Boto3 Route 53 client.

    Returns:
        str: ACM Certificate ARN.
    """
    # Check for existing certificate first
    existing_cert = get_existing_certificate(domain, acm_client)
    if existing_cert:
        # If certificate is already issued, return it
        cert_details = acm_client.describe_certificate(CertificateArn=existing_cert)
        if cert_details["Certificate"]["Status"] == "ISSUED":
            return existing_cert
        # If pending validation, continue with validation process
        cert_arn = existing_cert
        logger.info("Using existing certificate pending validation: %s", cert_arn)
    else:
        # Request new certificate
        response = acm_client.request_certificate(
            DomainName=domain,
            SubjectAlternativeNames=[f"www.{domain}"],
            ValidationMethod="DNS",
        )
        cert_arn = response["CertificateArn"]
        logger.info("Certificate requested with ARN: %s", cert_arn)

    # Retrieve validation options
    while True:
        cert_details = acm_client.describe_certificate(CertificateArn=cert_arn)
        cert_status = cert_details["Certificate"]["Status"]

        # If already issued, no need to validate
        if cert_status == "ISSUED":
            logger.info("Certificate already issued.")
            return cert_arn

        options = cert_details["Certificate"].get("DomainValidationOptions", [])
        if options and "ResourceRecord" in options[0]:
            break
        logger.info("Waiting for validation options to become available...")
        time.sleep(5)

    # Create DNS validation records for all domains
    for option in options:
        validation_record = option["ResourceRecord"]
        route53_client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                "Changes": [
                    {
                        "Action": "UPSERT",
                        "ResourceRecordSet": {
                            "Name": validation_record["Name"],
                            "Type": validation_record["Type"],
                            "TTL": 300,
                            "ResourceRecords": [{"Value": validation_record["Value"]}],
                        },
                    }
                ]
            },
        )
        logger.info(
            "Validation record created for %s in Route 53.", validation_record["Name"]
        )

    # Wait for certificate validation
    while True:
        cert_details = acm_client.describe_certificate(CertificateArn=cert_arn)
        status = cert_details["Certificate"]["Status"]
        if status == "ISSUED":
            logger.info("Certificate issued successfully.")
            break
        logger.info("Waiting for certificate validation (status: %s)...", status)
        time.sleep(15)

    return cert_arn


def get_kms_key(client, alias_name):
    """
    Check for an existing KMS alias and return the associated key ID if found.

    Args:
        client: Boto3 KMS client.
        alias_name: The name of the KMS alias to check.

    Returns:
        str: The key ID associated with the alias, or None if not found.
    """
    response = client.list_aliases()
    for alias in response["Aliases"]:
        if alias["AliasName"] == alias_name:
            logger.info("KMS alias %s already exists. Using existing key.", alias_name)
            return alias["TargetKeyId"]
    return None


def upload_index_html(s3_client, bucket_name, file_path):
    """
    Upload index.html to the specified S3 bucket.

    Args:
        s3_client: Boto3 S3 client.
        bucket_name: The S3 bucket name.
        file_path: Path to the index.html file.
    """
    logger.info("Uploading %s to bucket %s as %s...", file_path, bucket_name, file_path)
    s3_client.upload_file(
        file_path, bucket_name, file_path, ExtraArgs={"ContentType": "text/html"}
    )
    logger.info("Uploaded %s to bucket %s as %s.", file_path, bucket_name, file_path)


def main():
    """
    Main function to deploy the CloudFormation stack for the website framework.
    """
    parser = argparse.ArgumentParser(
        description="Deploy CloudFormation stack for website framework."
    )
    parser.add_argument(
        "--account",
        required=False,
        default=None,
        help="AWS named profile to use. Optional in CI where credentials are set via environment.",
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region to deploy to. Default is us-east-1.",
    )
    parser.add_argument(
        "--domain", required=True, help="The domain name to use for the website."
    )
    parser.add_argument(
        "--prefix", required=True, help="The project prefix for resource naming."
    )
    parser.add_argument(
        "--bucketlogslifecycle",
        default="365",
        help="Number of days to retain bucket logs. Default is 365.",
    )
    parser.add_argument(
        "--buckettransitionlifecycle",
        default="30",
        help="Number of days to transition logs. Default is 30.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate the CloudFormation template instead of deploying.",
    )

    args = parser.parse_args()

    # Configure AWS session (use profile if provided, otherwise use default credential chain)
    if args.account:
        boto3.setup_default_session(profile_name=args.account, region_name=args.region)
    else:
        boto3.setup_default_session(region_name=args.region)
    cfn_client = boto3.client("cloudformation")
    route53_client = boto3.client("route53")
    acm_client = boto3.client("acm")
    s3_client = boto3.client("s3")

    # Get hosted zone ID
    domain = args.domain
    zone_id_response = route53_client.list_hosted_zones_by_name(
        DNSName=domain, MaxItems="1"
    )
    hosted_zones = zone_id_response.get("HostedZones", [])
    if not hosted_zones or domain not in hosted_zones[0]["Name"]:
        raise ValueError(f"No hosted zone found for domain {domain}")
    hosted_zone_id = hosted_zones[0]["Id"].split("/")[-1]

    # Request ACM certificate
    acm_certificate_arn = request_acm_certificate(
        domain, hosted_zone_id, acm_client, route53_client
    )

    # Read the CloudFormation template
    with open("cfn-website-framework.yaml", "r", encoding="utf-8") as file:
        template_body = file.read()

    # Validate the template if requested
    if args.validate:
        validate_template(cfn_client, template_body)
        return

    # Deploy the stack
    stack_name = f"{args.prefix}-website-framework"
    deploy_stack(
        cfn_client,
        stack_name=stack_name,
        template_body=template_body,
        parameters=[
            {
                "ParameterKey": "ACMCertificateArn",
                "ParameterValue": acm_certificate_arn,
            },
            {"ParameterKey": "DomainName", "ParameterValue": args.domain},
            {"ParameterKey": "ProjectPrefix", "ParameterValue": args.prefix},
            {
                "ParameterKey": "BucketLogsLifeCycle",
                "ParameterValue": args.bucketlogslifecycle,
            },
            {
                "ParameterKey": "BucketTransitionLifeCycle",
                "ParameterValue": args.buckettransitionlifecycle,
            },
            {"ParameterKey": "HostedZoneId", "ParameterValue": hosted_zone_id},
        ],
    )

    # Upload html to S3
    upload_index_html(s3_client, args.domain, "index.html")
    upload_index_html(s3_client, args.domain, "resume.html")


if __name__ == "__main__":
    main()
