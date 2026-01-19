# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository hosts the crofton.cloud portfolio website infrastructure. It demonstrates AWS infrastructure-as-code with NIST 800-53 compliance patterns using CloudFormation for a static website with S3, CloudFront, ACM, and Route 53.

## Common Commands

### Linting

```bash
# CloudFormation template linting
cfn-lint cloudformation/**/*.yaml

# CloudFormation security scanning
cfn_nag_scan --input-path cloudformation

# Python linting (C0301 line-length disabled)
pylint --disable=C0301 **/*.py
```

### Deployment

Run from the `cloudformation/` directory:

```bash
python3 ./deploy.py --account <AWS_PROFILE> --region us-east-1 --domain <DOMAIN> --prefix <PREFIX>

# Optional parameters:
#   --bucketlogslifecycle <days>       Log retention (default: 365)
#   --buckettransitionlifecycle <days> Storage transition (default: 30)
#   --validate                         Validate template only, don't deploy
```

### Dependencies

```bash
pip install -r requirements.txt  # boto3, botocore, pylint, requests
pip install cfn-lint             # CloudFormation linter
gem install cfn-nag              # CloudFormation security scanner (requires Ruby)
```

## Architecture

**deploy.py** orchestrates the full deployment:
1. Looks up Route 53 hosted zone for the domain
2. Requests ACM certificate with DNS validation (creates Route 53 records automatically)
3. Waits for certificate issuance
4. Deploys/updates CloudFormation stack with certificate ARN
5. Uploads HTML files to S3

**cfn-website-framework.yaml** creates:
- S3 bucket for website hosting (with versioning, encryption, public access blocking)
- S3 buckets for S3 and CloudFront access logging
- CloudFront distribution with custom SSL certificate
- Route 53 DNS records pointing to CloudFront
- SQS queue with dead-letter queue for S3 event notifications

## CI/CD

- **Push to any branch**: Runs cfn-lint, cfn-nag, and pylint (stdout only)
- **PR to main**: Same linting plus posts results as PR comments

All linting jobs use `|| true` to report issues without failing the pipeline.

## Prerequisites

- AWS CLI configured with a named profile
- Route 53 hosted zone must already exist for the target domain
- IAM permissions for ACM, CloudFormation, Route 53, S3, and KMS
