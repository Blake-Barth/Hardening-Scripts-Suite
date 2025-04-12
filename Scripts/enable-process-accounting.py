#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def run_command(cmd, description=None):
    if description:
        print(description)
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {' '.join(cmd)} completed.")
    except subprocess.CalledProcessError:
        print(f"❌ Failed: {' '.join(cmd)}")

def install_acct():
    run_command(["apt-get", "update"], "📦 Updating package lists...")
    run_command(["apt-get", "install", "-y", "acct"], "🔧 Installing process accounting tools...")

def enable_accounting():
    run_command(["accton", "on"], "📈 Enabling process accounting...")
    print("📂 Log file: /var/account/pacct")

def verify_accounting():
    result = subprocess.run(["accton"], capture_output=True, text=True)
    if "/var/account/pacct" in result.stdout:
        print("✅ Process accounting is active.")
    else:
        print("⚠️  Process accounting does not appear to be active.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🧮 This script enables process accounting using the `acct` package.")

    if not confirm("Do you want to enable process accounting on this system?"):
        print("❎ Aborted by user.")
        return

    install_acct()
    enable_accounting()
    verify_accounting()

if __name__ == "__main__":
    main()
