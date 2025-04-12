#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil

LIMITS_CONF = "/etc/security/limits.conf"
SYSCTL_CONF = "/etc/sysctl.d/99-disable-coredump.conf"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
        print(f"🗂️  Backed up {path} to {path}.bak")

def update_limits_conf():
    print(f"🔧 Updating {LIMITS_CONF} to disable core dumps...")
    backup_file(LIMITS_CONF)

    new_lines = [
        "* hard core 0",
        "* soft core 0"
    ]

    updated = False
    with open(LIMITS_CONF, "r") as f:
        lines = f.readlines()

    # Remove any existing 'core' settings
    filtered_lines = [line for line in lines if " core " not in line]

    # Append new settings
    filtered_lines.extend([line + "\n" for line in new_lines])

    with open(LIMITS_CONF, "w") as f:
        f.writelines(filtered_lines)

    print(f"✅ Core dump limits added directly to {LIMITS_CONF}")

def write_sysctl_conf():
    content = "fs.suid_dumpable = 0\n"
    print(f"🔧 Writing to {SYSCTL_CONF}...")
    with open(SYSCTL_CONF, "w") as f:
        f.write(content)
    subprocess.run(["sysctl", "-p", SYSCTL_CONF], check=True)
    print("✅ Applied sysctl setting: fs.suid_dumpable = 0")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔒 This script will disable core dumps system-wide by editing:")
    print(f" - {LIMITS_CONF}")
    print(f" - {SYSCTL_CONF}")

    if not confirm("Do you want to continue?"):
        print("❎ Aborted by user.")
        return

    try:
        update_limits_conf()
        write_sysctl_conf()
        print("✅ Core dumps have been disabled and settings applied.")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
