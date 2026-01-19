# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository hosts the crofton.cloud portfolio website infrastructure. It demonstrates AWS infrastructure-as-code with NIST 800-53 compliance patterns using CloudFormation for a static website with S3, CloudFront, Lambda, API Gateway, and SES.

## Repository Structure

```
.
├── .github/
│   ├── CODEOWNERS              # Code ownership for PR reviews
│   └── workflows/
│       ├── deploy.yml          # AWS deployment (main branch only)
│       ├── lint_on_*.yaml      # Linting workflows
│       └── sast.yml            # Security scanning with portfolio-code-scanner
├── cloudformation/
│   ├── cfn-website-framework.yaml    # Main infrastructure (S3, CloudFront, Route53)
│   ├── cfn-contact-form.yaml         # Contact form (Lambda, API Gateway, KMS)
│   ├── github-oidc-deploy-role.yaml  # GitHub Actions OIDC IAM role
│   └── deploy.py                     # Manual deployment script
├── data/
│   └── resume.yaml             # Structured resume data for site generation
├── lambda/
│   └── contact_form.py         # Lambda handler for contact form
├── site/
│   ├── generate.py             # Static site generator (Jinja2)
│   ├── templates/              # HTML templates
│   └── static/                 # CSS and static assets
└── dist/                       # Generated site output (gitignored)
```

## Common Commands

### Linting

```bash
# CloudFormation linting
cfn-lint cloudformation/*.yaml

# CloudFormation security scanning
cfn_nag_scan --input-path cloudformation/

# Python linting
pylint --disable=C0301 **/*.py

# Run all pre-commit hooks
pre-commit run --all-files
```

### Site Generation

```bash
cd site
python3 generate.py --output-dir ../dist --api-endpoint <API_ENDPOINT>
```

### Manual Deployment

Run from the `cloudformation/` directory:

```bash
# Local deployment with AWS profile
python3 ./deploy.py --account <AWS_PROFILE> --region us-east-1 --domain <DOMAIN> --prefix <PREFIX>

# CI/CD deployment (uses OIDC credentials from environment)
python3 ./deploy.py --region us-east-1 --domain <DOMAIN> --prefix <PREFIX>

# Optional parameters:
#   --account <AWS_PROFILE>            AWS named profile (optional in CI)
#   --bucketlogslifecycle <days>       Log retention (default: 365)
#   --buckettransitionlifecycle <days> Storage transition (default: 30)
#   --validate                         Validate template only
```

### Dependencies

```bash
pip install -r requirements.txt  # boto3, botocore, Jinja2, PyYAML, pylint, requests
pip install cfn-lint             # CloudFormation linter
gem install cfn-nag              # CloudFormation security scanner (requires Ruby)
pre-commit install               # Install git hooks
```

## Architecture

### Website Infrastructure (cfn-website-framework.yaml)

- S3 bucket for website hosting (KMS encryption, versioning, public access blocking)
- S3 buckets for access logging (S3 and CloudFront)
- CloudFront distribution with custom SSL certificate
- Route 53 DNS records (apex and www)
- SQS queue with DLQ for S3 event notifications

### Contact Form (cfn-contact-form.yaml)

- Lambda function for form submissions
- API Gateway HTTP API with CORS
- KMS key for environment variable and log encryption
- CloudWatch Log Groups with KMS encryption
- SES integration for email delivery

### GitHub Actions OIDC (github-oidc-deploy-role.yaml)

- IAM role for GitHub Actions with OIDC trust
- Scoped policies for CloudFormation, S3, CloudFront, Route53, ACM, KMS, Lambda, API Gateway, SES, SQS

## CI/CD

### Branching Strategy (GitHub Flow)

- `main` - Production branch, always deployable
- `feature/*` - Feature branches (PR to main)

All changes go through pull requests to main. Merging to main triggers deployment.

### Workflows

- **Push to any branch**: Linting (cfn-lint, cfn-nag, pylint)
- **PR to main**: SAST scanning, lint comments posted to PR
- **Push to main**: Full AWS deployment via OIDC

### Pre-commit Hooks

- Trailing whitespace, EOF fixes
- YAML validation, large file check
- Private key detection
- cfn-lint, black, flake8, pylint

## Prerequisites

- AWS CLI configured with a named profile
- Route 53 hosted zone for the target domain
- GitHub repository secrets: `AWS_ACCOUNT_ID`
- SES email verification for sender/recipient addresses
