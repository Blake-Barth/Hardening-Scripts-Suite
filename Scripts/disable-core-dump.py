#!/usr/bin/env python3

import os
import sys
import subprocess

LIMITS_FILE = "/etc/security/limits.d/99-disable-coredump.conf"
SYSCTL_FILE = "/etc/sysctl.d/99-disable-coredump.conf"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def write_limits_conf():
    content = (
        "* hard core 0\n"
        "* soft core 0\n"
    )
    with open(LIMITS_FILE, "w") as f:
        f.write(content)
    print(f"✅ Wrote core dump limits to {LIMITS_FILE}")

def write_sysctl_conf():
    content = "fs.suid_dumpable = 0\n"
    with open(SYSCTL_FILE, "w") as f:
        f.write(content)
    print(f"✅ Wrote sysctl setting to {SYSCTL_FILE}")
    subprocess.run(["sysctl", "-p", SYSCTL_FILE], check=True)
    print("🔄 Applied sysctl setting immediately")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔒 This script will disable core dumps system-wide.")
    print("This prevents sensitive memory contents from being written to disk.")

    if not confirm("Do you want to continue?"):
        print("❎ Aborted by user.")
        return

    try:
        write_limits_conf()
        write_sysctl_conf()
        print("✅ Core dumps disabled system-wide.")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
