"""
Lambda function to handle contact form submissions.

Receives POST requests from the website contact form, validates input,
and sends an email via Amazon SES.
"""

import base64
import json
import logging
import os
import re

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "*")

# SES client
ses_client = boto3.client("ses")

# Email regex pattern
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_email(email):
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email))


def sanitize_input(text):
    """Sanitize input by removing potentially harmful characters."""
    if not text:
        return ""
    # Remove HTML tags and limit length
    sanitized = re.sub(r"<[^>]*>", "", str(text))
    return sanitized[:5000]  # Limit to 5000 characters


def build_response(status_code, body, origin=None):
    """Build HTTP response with CORS headers."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": origin or ALLOWED_ORIGIN,
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        },
        "body": json.dumps(body),
    }


def send_email(name, email, message):
    """Send email via SES."""
    subject = f"Contact Form Submission from {name}"
    body_text = f"""
New contact form submission:

Name: {name}
Email: {email}

Message:
{message}
"""
    body_html = f"""
<html>
<head></head>
<body>
<h2>New Contact Form Submission</h2>
<p><strong>Name:</strong> {name}</p>
<p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
<h3>Message:</h3>
<p>{message.replace(chr(10), '<br>')}</p>
</body>
</html>
"""

    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={"ToAddresses": [RECIPIENT_EMAIL]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
            ReplyToAddresses=[email],
        )
        logger.info("Email sent successfully. MessageId: %s", response["MessageId"])
        return True
    except ClientError as err:
        logger.error("Failed to send email: %s", err.response["Error"]["Message"])
        return False


def parse_request_body(event):
    """Parse the request body from the event."""
    raw_body = event.get("body", "")
    if not raw_body:
        return {}

    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    return json.loads(raw_body)


def validate_form_fields(name, email, message):
    """Validate form fields and return list of errors."""
    errors = []
    if not name or len(name) < 2:
        errors.append("Name is required (minimum 2 characters)")
    if not email:
        errors.append("Email is required")
    elif not validate_email(email):
        errors.append("Invalid email format")
    if not message or len(message) < 10:
        errors.append("Message is required (minimum 10 characters)")
    return errors


def handler(event, _context):
    """Lambda handler for contact form submissions."""
    logger.info("Received event: %s", json.dumps(event))

    # Handle OPTIONS preflight request
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return build_response(200, {"message": "OK"})

    # Parse request body
    try:
        body = parse_request_body(event)
    except json.JSONDecodeError as err:
        logger.error("Failed to parse request body: %s", err)
        return build_response(400, {"error": "Invalid JSON in request body"})

    # Extract and validate fields
    name = sanitize_input(body.get("name", ""))
    email = sanitize_input(body.get("email", ""))
    message = sanitize_input(body.get("message", ""))

    errors = validate_form_fields(name, email, message)
    if errors:
        return build_response(400, {"error": "Validation failed", "details": errors})

    # Check environment configuration
    if not RECIPIENT_EMAIL or not SENDER_EMAIL:
        logger.error(
            "Missing environment configuration: RECIPIENT_EMAIL or SENDER_EMAIL"
        )
        return build_response(500, {"error": "Server configuration error"})

    # Send email
    if send_email(name, email, message):
        return build_response(
            200, {"message": "Thank you for your message. I will get back to you soon."}
        )

    return build_response(
        500, {"error": "Failed to send message. Please try again later."}
    )
