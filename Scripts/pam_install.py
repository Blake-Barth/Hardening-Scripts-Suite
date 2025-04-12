#!/usr/bin/env python3

import subprocess
import os
import sys
import shutil
import re

PAM_FILE = "/etc/pam.d/common-password"
MODULE_NAME = "pam_pwquality.so"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
        print(f"🗂️  Backed up {path} to {path}.bak")

def install_pwquality():
    print("📦 Installing libpam-pwquality...")
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt-get", "install", "-y", "libpam-pwquality"], check=True)
    print("✅ libpam-pwquality installed.")

def update_pam_config():
    print(f"🔧 Updating {PAM_FILE} to enforce strong password policy...")
    backup_file(PAM_FILE)

    with open(PAM_FILE, "r") as f:
        lines = f.readlines()

    pattern = re.compile(r"^password\s+requisite\s+.*pam_pwquality\.so")
    modified = False

    for i, line in enumerate(lines):
        if pattern.search(line):
            # Update existing line with stronger options
            lines[i] = (
                "password requisite pam_pwquality.so retry=3 minlen=12 difok=3 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1\n"
            )
            modified = True
            break

    if not modified:
        # Add it before the first "password" line or at the end
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("password"):
                lines.insert(i, "password requisite pam_pwquality.so retry=3 minlen=12 difok=3 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1\n")
                inserted = True
                break
        if not inserted:
            lines.append("password requisite pam_pwquality.so retry=3 minlen=12 difok=3 ucredit=-1 lcredit=-1 dcredit=-1 ocredit=-1\n")

    with open(PAM_FILE, "w") as f:
        f.writelines(lines)

    print("✅ PAM password strength policy enforced.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔐 This script will:")
    print("  - Install libpam-pwquality for password strength enforcement")
    print("  - Update PAM config to require strong passwords")

    if not confirm("Do you want to proceed?"):
        print("❎ Aborted by user.")
        return

    try:
        install_pwquality()
        update_pam_config()
        print("✅ PAM password strength hardening complete.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
