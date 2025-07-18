#!/usr/bin/env python3
"""
OpenAPI Schema Export Utility

This script exports the OpenAPI JSON schema from the FastAPI application
to a file that can be used for documentation, code generation, or API testing.

Usage:
    python scripts/export_openapi.py [--output openapi/poshub_v1.json] [--pretty]

Options:
    --output FILE    Output file path (default: openapi/poshub_v1.json)
    --pretty         Pretty-print the JSON output
    --help           Show this help message
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path to import the FastAPI app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import app


def export_openapi_schema(output_path: str, pretty: bool = False) -> None:
    """
    Export OpenAPI schema to a JSON file

    Args:
        output_path: Path where to save the OpenAPI JSON
        pretty: Whether to pretty-print the JSON output
    """
    try:
        # Get OpenAPI schema from FastAPI app
        openapi_schema = app.openapi()

        # Prepare JSON serialization options
        json_options = {
            "ensure_ascii": False,
            "separators": (",", ":") if not pretty else None,
            "indent": 2 if pretty else None,
        }

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, **json_options)

        print(f"✅ OpenAPI schema exported to: {output_file.absolute()}")

        # Print some stats
        schema_info = {
            "title": openapi_schema.get("info", {}).get("title", "Unknown"),
            "version": openapi_schema.get("info", {}).get("version", "Unknown"),
            "paths": len(openapi_schema.get("paths", {})),
            "tags": len(openapi_schema.get("tags", [])),
            "components": len(
                openapi_schema.get("components", {}).get("schemas", {})
            ),
        }

        print("\n📊 Schema Statistics:")
        print(f"   Title: {schema_info['title']}")
        print(f"   Version: {schema_info['version']}")
        print(f"   Endpoints: {schema_info['paths']}")
        print(f"   Tags: {schema_info['tags']}")
        print(f"   Components: {schema_info['components']}")

    except Exception as e:
        print(f"❌ Error exporting OpenAPI schema: {e}")
        sys.exit(1)


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Export OpenAPI JSON schema from FastAPI application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Export to default file
    python scripts/export_openapi.py

    # Export to custom file with pretty printing
    python scripts/export_openapi.py --output docs/api-schema.json --pretty

    # Export for use with code generators
    python scripts/export_openapi.py --output openapi/poshub_v1.json --pretty
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        default="openapi/poshub_v1.json",
        help="Output file path (default: openapi/poshub_v1.json)",
    )

    parser.add_argument(
        "--pretty", "-p", action="store_true", help="Pretty-print the JSON output"
    )

    args = parser.parse_args()

    print("🚀 Exporting OpenAPI schema...")
    export_openapi_schema(args.output, args.pretty)


if __name__ == "__main__":
    main() 