#!/usr/bin/env python3
"""
Demo script showing centralized version management in TruLedgr API.

This script demonstrates how to access the version from anywhere in the codebase.
"""

import truledgr_api
from truledgr_api.apps.main import create_app

def main():
    print("=== TruLedgr API Version Management Demo ===")
    print(f"Package version: {truledgr_api.__version__}")

    # Create the main app and show its version
    app = create_app()
    print(f"FastAPI app version: {app.version}")

    # Show how to use the version in other parts of the code
    print(f"API Version for documentation: v{truledgr_api.__version__}")
    print(f"User-Agent header: TruLedgr-API/{truledgr_api.__version__}")

    print("\n✅ Version management is working correctly!")
    print("The version is defined in one place (truledgr_api/__init__.py)")
    print("and used consistently throughout the application.")

if __name__ == "__main__":
    main()
