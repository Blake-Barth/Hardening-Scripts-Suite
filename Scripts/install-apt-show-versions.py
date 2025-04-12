#!/usr/bin/env python3

import os
import sys
import subprocess

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def run_command(cmd):
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {' '.join(cmd)} completed.")
    except subprocess.CalledProcessError:
        print(f"❌ Command failed: {' '.join(cmd)}")

def install_apt_show_versions():
    print("📦 Installing apt-show-versions...")
    run_command(["apt-get", "update"])
    run_command(["apt-get", "install", "-y", "apt-show-versions"])

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔍 This script installs `apt-show-versions` to audit package versions.")

    if not confirm("Do you want to install apt-show-versions?"):
        print("❎ Aborted by user.")
        return

    install_apt_show_versions()

    print("🎉 Done.")

if __name__ == "__main__":
    main()
