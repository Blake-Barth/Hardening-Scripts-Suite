#!/usr/bin/env python3

import os
import sys
import subprocess

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def run_command(command):
    try:
        subprocess.run(command, check=True)
        print(f"✅ {' '.join(command)} completed.")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to run: {' '.join(command)}")

def install_unattended_upgrades():
    print("📦 Installing unattended-upgrades package...")
    run_command(["apt-get", "install", "-y", "unattended-upgrades"])

    print("🔧 Enabling automatic updates...")
    run_command(["dpkg-reconfigure", "--priority=low", "unattended-upgrades"])

    print("✅ Unattended upgrades enabled.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("📦 This script will help you update your system securely using apt.")

    if confirm("Do you want to run `apt-get update`?"):
        run_command(["apt-get", "update"])

    if confirm("Do you want to run `apt-get upgrade`?"):
        run_command(["apt-get", "upgrade", "-y"])

    if confirm("Do you want to run `apt-get dist-upgrade`?"):
        run_command(["apt-get", "dist-upgrade", "-y"])

    if confirm("Do you want to enable unattended-upgrades for automatic security updates?"):
        install_unattended_upgrades()

    print("\n🎉 All selected updates complete.")

if __name__ == "__main__":
    main()
