#!/usr/bin/env python3
"""
Static site generator for crofton.cloud.

Reads structured data from data/resume.yaml and generates HTML pages
using Jinja2 templates.

Usage:
    python generate.py [--output-dir OUTPUT_DIR] [--api-endpoint API_ENDPOINT]

Example:
    python generate.py --output-dir ../dist --api-endpoint https://api.example.com/contact
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


def load_resume_data(data_path):
    """Load resume data from YAML file."""
    with open(data_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def create_jinja_env(templates_dir):
    """Create Jinja2 environment with templates."""
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_pages(env, data, output_dir, api_endpoint):
    """Generate all HTML pages."""
    pages = [
        ("index.html", "index.html", {"page": "home"}),
        ("resume.html", "resume.html", {"page": "resume"}),
        ("services.html", "services.html", {"page": "services"}),
        ("architecture.html", "architecture.html", {"page": "architecture"}),
        (
            "contact.html",
            "contact.html",
            {"page": "contact", "api_endpoint": api_endpoint},
        ),
    ]

    for template_name, output_name, extra_context in pages:
        template = env.get_template(template_name)
        context = {**data, **extra_context}
        html = template.render(**context)

        output_path = output_dir / output_name
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html)
        print(f"Generated: {output_path}")


def copy_static_files(static_dir, output_dir):
    """Copy static files (CSS, JS, images) to output directory."""
    if not static_dir.exists():
        return

    for item in static_dir.iterdir():
        dest = output_dir / item.name
        if item.is_file():
            shutil.copy2(item, dest)
            print(f"Copied: {dest}")
        elif item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)
            print(f"Copied directory: {dest}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate static site from resume data"
    )
    parser.add_argument(
        "--data-file",
        default="../data/resume.yaml",
        help="Path to resume YAML file (default: ../data/resume.yaml)",
    )
    parser.add_argument(
        "--output-dir",
        default="../dist",
        help="Output directory for generated files (default: ../dist)",
    )
    parser.add_argument(
        "--api-endpoint",
        default="{{API_ENDPOINT}}",
        help="Contact form API endpoint (default: placeholder for CI injection)",
    )
    args = parser.parse_args()

    # Resolve paths relative to script location
    script_dir = Path(__file__).parent
    data_path = (script_dir / args.data_file).resolve()
    output_dir = (script_dir / args.output_dir).resolve()
    templates_dir = script_dir / "templates"
    static_dir = script_dir / "static"

    # Validate paths
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}", file=sys.stderr)
        sys.exit(1)

    if not templates_dir.exists():
        print(f"Error: Templates directory not found: {templates_dir}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"Loading data from: {data_path}")
    data = load_resume_data(data_path)

    # Create Jinja environment
    env = create_jinja_env(templates_dir)

    # Generate pages
    print(f"Generating pages to: {output_dir}")
    generate_pages(env, data, output_dir, args.api_endpoint)

    # Copy static files
    copy_static_files(static_dir, output_dir)

    print("Site generation complete!")


if __name__ == "__main__":
    main()
