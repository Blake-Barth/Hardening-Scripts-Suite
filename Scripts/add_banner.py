#!/usr/bin/env python3

import os
import sys

# Paths to the files to modify
ISSUE_FILE = "/etc/issue"
ISSUE_NET_FILE = "/etc/issue.net"

# Banner text
BANNER_TEXT = """
*****************************************************
*                                                   *
*     Welcome to Your Secure System                *
*     Unauthorized access is prohibited            *
*     Please contact admin@example.com for support *
*                                                   *
*****************************************************
"""

def confirm(prompt):
    """Ask the user for confirmation."""
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def append_banner(file_path, banner):
    """Append the banner to the given file."""
    try:
        with open(file_path, "a") as f:
            f.write(banner)
        print(f"✅ Banner added to {file_path}")
    except Exception as e:
        print(f"❌ Error writing to {file_path}: {e}")

def main():
    # Check if the script is run as root (for sudo access)
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("⚠️ This script will add a custom banner to the following files:")
    print(f"  • {ISSUE_FILE}")
    print(f"  • {ISSUE_NET_FILE}")

    if not confirm("Do you want to continue and add the banner?"):
        print("❎ Aborted by user.")
        return

    try:
        # Append the banner to /etc/issue and /etc/issue.net
        append_banner(ISSUE_FILE, BANNER_TEXT)
        append_banner(ISSUE_NET_FILE, BANNER_TEXT)
        
        print("✅ Banner successfully added to both files.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
