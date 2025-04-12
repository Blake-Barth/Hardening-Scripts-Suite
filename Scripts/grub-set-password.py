#!/usr/bin/env python3

import subprocess
import getpass
import sys
import os

GRUB_DEFAULT = "/etc/default/grub"
GRUB_CUSTOM = "/etc/grub.d/40_custom"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def ensure_grub_default_setting(key, value):
    updated = False
    if not os.path.exists(GRUB_DEFAULT):
        print(f"❌ {GRUB_DEFAULT} not found.")
        return

    with open(GRUB_DEFAULT, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f'{key}="{value}"\n'
            updated = True
            break

    if not updated:
        lines.append(f'{key}="{value}"\n')

    with open(GRUB_DEFAULT, "w") as f:
        f.writelines(lines)
    
    print(f"✅ Set {key}={value} in {GRUB_DEFAULT}")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔐 This script will protect your GRUB bootloader with a password.")
    print("This prevents unauthorized modification of boot options.")

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

        with open(GRUB_CUSTOM, "a") as f:
            f.write(entry)

        print(f"✅ GRUB password entry appended to {GRUB_CUSTOM}")

        # Apply additional protections
        ensure_grub_default_setting("GRUB_DISABLE_RECOVERY", "true")
        ensure_grub_default_setting("GRUB_ENABLE_CRYPTODISK", "y")

        print("🔄 Updating GRUB config...")
        subprocess.run(['update-grub'], check=True)
        print("✅ GRUB configuration updated successfully.")

        print("\n📌 Reboot your system to test GRUB password protection.")
        print("   Try pressing 'e' or entering recovery mode — it should now require authentication.")

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
    except Exception as ex:
        print(f"❌ Unexpected error: {ex}")

if __name__ == "__main__":
    main()
