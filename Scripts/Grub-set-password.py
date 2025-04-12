#!/usr/bin/env python3

import subprocess
import getpass
import sys
import os

def confirm(prompt):
    resp = input(f"{prompt} (y/n): ").strip().lower()
    return resp == 'y'

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔐 This script will set a password for the GRUB bootloader.")
    print("This helps prevent unauthorized users from modifying boot options.")

    if not confirm("Do you want to continue?"):
        print("❎ Aborted by user.")
        return

    try:
        password = getpass.getpass("Enter new GRUB password: ")
        confirm_password = getpass.getpass("Confirm password: ")

        if password != confirm_password:
            print("❌ Passwords do not match. Exiting.")
            return

        print("🔄 Hashing password using grub-mkpasswd-pbkdf2...")
        result = subprocess.run(['grub-mkpasswd-pbkdf2'], input=f"{password}\n{password}\n",
                                text=True, capture_output=True, check=True)
        for line in result.stdout.splitlines():
            if "grub.pbkdf2" in line:
                grub_hash = line.strip()
                break
        else:
            print("❌ Could not extract GRUB password hash.")
            return

        entry = (
            '\n# Set GRUB superuser and hashed password\n'
            'set superuser="admin"\n'
            f'password_pbkdf2 admin {grub_hash}\n'
        )

        grub_file = "/etc/grub.d/40_custom"
        with open(grub_file, "a") as f:
            f.write(entry)

        print(f"✅ GRUB password entry appended to {grub_file}")

        print("🔄 Updating GRUB config...")
        subprocess.run(['update-grub'], check=True)
        print("✅ GRUB configuration updated successfully.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
    except Exception as ex:
        print(f"❌ Unexpected error: {ex}")

if __name__ == "__main__":
    main()
