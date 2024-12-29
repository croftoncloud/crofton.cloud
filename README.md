# crofton.cloud
crofton.cloud demo infrastructure

This repository will host demo content for the services offered by crofton.cloud.

Initial examples to include:

- CloudFormation: public S3 website setup with cloudfront, ACM, and all NIST 800-53 controls satisfied.
- DNS Review including SPK/DKIM/MX
- Documentation Samples

## Assets

*cfn-website-framework.yaml*

Parameters:
    - ACMCertificateArn
    - BucketLogsLifeCycle
    - BucketTransitionLifeCycle
    - DomainName
    - HostedZoneId
    - ProjectPrefix

Resources:
    - KMS Key
    - S3 Bucket for Hosting
    - S3 Bucket for S3 Access Logging
    - S3 Bucket for CloudFront Access Logging
    - SQS Queue for Event Notifications
    - CloudFront Distribution to serve content
    - Route 53 Records to map domain to CloudFront Distribution

*deploy.py*

Usage: `usage: deploy.py [-h] --account ACCOUNT [--region REGION] --domain DOMAIN --prefix PREFIX [--bucketlogslifecycle BUCKETLOGSLIFECYCLE] [--buckettransitionlifecycle BUCKETTRANSITIONLIFECYCLE] [--validate] [--index-file INDEX_FILE]`

Example usage:

```
python3 ./deploy.py --account portfolio --region us-east-1 --domain crofton.cloud --prefix cc
Certificate requested with ARN: arn:aws:acm:us-east-1:918573727633:certificate/c4cafdfc-8b21-4ab4-bc50-f88c52a5cf71
Validation record created for _b40c66fde266885c2a569ccfe97e0859.crofton.cloud. in Route 53.
Validation record created for _0a86bf8ffd997e1f651fd50e609b1ee7.www.crofton.cloud. in Route 53.
Certificate issued successfully.
Checking if stack cc-website-framework exists...
Stack cc-website-framework exists. Updating...
Stack cc-website-framework updated successfully.
Uploading ./index.html to bucket crofton.cloud...
Uploaded ./index.html to bucket crofton.cloud as index.html
```

This script collects information from the AWS tenant to provide input for CloudFormation. It also monitors the deployment process to assist with errors.

*index.html*

This is a basic HTML page used to validate successful deployment of all components. This page can be updated to have the actual site content.
