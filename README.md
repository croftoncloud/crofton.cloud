# crofton.cloud

Portfolio website demonstrating AWS infrastructure-as-code with NIST 800-53 compliance patterns.

## Features

- **Static Site Generator** - Jinja2-based generator using structured YAML data
- **Serverless Contact Form** - Lambda + API Gateway + SES with KMS encryption
- **Infrastructure as Code** - CloudFormation templates with security best practices
- **CI/CD Pipeline** - GitHub Actions with OIDC authentication (no stored credentials)
- **Security Scanning** - Automated SAST with checkov, cfn-nag, and portfolio-code-scanner

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Route 53  │────▶│  CloudFront │────▶│     S3      │
│   (DNS)     │     │   (CDN)     │     │  (Website)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  API Gateway│────▶│   Lambda    │────▶│     SES     │
│  (HTTP API) │     │  (Contact)  │     │   (Email)   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Quick Start

### Prerequisites

- AWS CLI configured with a named profile
- Route 53 hosted zone for your domain
- Python 3.12+, Ruby (for cfn-nag)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install linting tools
pip install cfn-lint
gem install cfn-nag

# Install pre-commit hooks
pre-commit install
```

### Generate Site Locally

```bash
cd site
python3 generate.py --output-dir ../dist
```

### Deploy Infrastructure

```bash
cd cloudformation
# Local deployment with AWS profile
python3 deploy.py --account <AWS_PROFILE> --domain <DOMAIN> --prefix <PREFIX>

# CI/CD deployment (uses OIDC credentials from environment)
python3 deploy.py --domain <DOMAIN> --prefix <PREFIX>
```

## Repository Structure

```
├── .github/workflows/     # CI/CD pipelines
├── cloudformation/        # AWS CloudFormation templates
│   ├── cfn-website-framework.yaml    # S3, CloudFront, Route53
│   ├── cfn-contact-form.yaml         # Lambda, API Gateway, KMS
│   └── github-oidc-deploy-role.yaml  # GitHub Actions IAM role
├── data/resume.yaml       # Structured content data
├── lambda/                # Lambda function code
├── site/                  # Static site generator
│   ├── generate.py        # Generator script
│   ├── templates/         # Jinja2 templates
│   └── static/            # CSS assets
└── dist/                  # Generated output (gitignored)
```

## CloudFormation Templates

### cfn-website-framework.yaml

| Resource | Description |
|----------|-------------|
| S3 Bucket | Website hosting with KMS encryption |
| S3 Logging Buckets | Access logs for S3 and CloudFront |
| CloudFront Distribution | CDN with custom SSL certificate |
| Route 53 Records | DNS for apex and www subdomain |
| SQS Queue | Event notifications with DLQ |
| KMS Key | Encryption for S3 objects |

### cfn-contact-form.yaml

| Resource | Description |
|----------|-------------|
| Lambda Function | Contact form handler |
| API Gateway HTTP API | REST endpoint with CORS |
| KMS Key | Encryption for env vars and logs |
| CloudWatch Log Groups | Execution and access logs |
| IAM Role | Lambda execution with SES permissions |

### github-oidc-deploy-role.yaml

| Resource | Description |
|----------|-------------|
| IAM Role | OIDC trust for GitHub Actions |
| IAM Policies | Scoped permissions for AWS services |

## CI/CD Workflows

| Workflow | Trigger | Actions |
|----------|---------|---------|
| Lint | Push to any branch | cfn-lint, cfn-nag, pylint |
| SAST | PR/Push to main | Security scanning with SARIF upload |
| Deploy | Push to main | Generate site, deploy CFN, sync S3, invalidate cache |

**Branching**: GitHub Flow - feature branches merge directly to main via PR.

## Security Features

- KMS encryption for S3, Lambda env vars, CloudWatch Logs
- Public access blocking on all S3 buckets
- SSL/TLS enforcement (HTTPS only)
- OIDC authentication (no long-lived credentials)
- Security scanning in CI pipeline
- Pre-commit hooks for local validation

## License

[PolyForm Noncommercial 1.0.0](LICENSE) - Free for non-commercial use.
