#!/usr/bin/env python3

import os
import sys
import subprocess

# Targets and their secure permission modes
PATHS = {
    "/etc/sudoers": "440",
    "/etc/sudoers.d": "750"  # could also use 700 for max lockdown
}

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def secure_permissions(path, mode):
    try:
        print(f"🔒 Securing {path}...")

        if not os.path.exists(path):
            print(f"⚠️  {path} does not exist. Skipping.")
            return

        subprocess.run(["chown", "root:root", path], check=True)
        subprocess.run(["chmod", mode, path], check=True)

        print(f"✅ Permissions set to {mode} and ownership to root:root for {path}")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to apply permissions to {path}")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🛡️  This script sets secure ownership and permissions on sudoers files.")

    for path, mode in PATHS.items():
        if confirm(f"Do you want to secure permissions for {path}?"):
            secure_permissions(path, mode)
        else:
            print(f"❎ Skipped {path}")

if __name__ == "__main__":
    main()
