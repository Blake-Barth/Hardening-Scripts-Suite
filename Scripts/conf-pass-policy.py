#!/usr/bin/env python3

import os
import sys
import shutil

LOGIN_DEFS = "/etc/login.defs"

DEFAULTS = {
    "PASS_MIN_DAYS": 1,
    "PASS_MAX_DAYS": 90,
    "SHA_CRYPT_MIN_ROUNDS": 5000,
    "SHA_CRYPT_MAX_ROUNDS": 10000
}

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
        print(f"🗂️  Backed up {path} to {path}.bak")

def set_or_update_param(lines, key, value):
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(key):
            lines[i] = f"{key}   {value}\n"
            updated = True
            break
    if not updated:
        lines.append(f"\n{key}   {value}\n")
    return lines

def apply_settings(config):
    print(f"🔧 Updating {LOGIN_DEFS} with policy values...")
    backup_file(LOGIN_DEFS)

    with open(LOGIN_DEFS, "r") as f:
        lines = f.readlines()

    for key, val in config.items():
        lines = set_or_update_param(lines, key, val)

    with open(LOGIN_DEFS, "w") as f:
        f.writelines(lines)

    print("✅ All settings applied successfully to /etc/login.defs.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔐 This script sets the following policies in /etc/login.defs:")
    for key, val in DEFAULTS.items():
        print(f"  • {key} = {val}")

    if not confirm("Do you want to continue and configure these settings?"):
        print("❎ Aborted by user.")
        return

    try:
        config = {}
        for key, default in DEFAULTS.items():
            user_input = input(f"Enter value for {key} (default {default}): ").strip()
            config[key] = int(user_input) if user_input.isdigit() else default

        apply_settings(config)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
