#!/usr/bin/env python3

import os
import sys
import subprocess

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def run_command(cmd, message=None):
    if message:
        print(message)
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ {' '.join(cmd)} completed.\n")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to run: {' '.join(cmd)}")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🛡️  This script installs and initializes Rootkit Hunter (rkhunter).")

    if not confirm("Do you want to install rkhunter?"):
        print("❎ Aborted by user.")
        return

    run_command(["apt-get", "update"], "📦 Updating package lists...")
    run_command(["apt-get", "install", "-y", "rkhunter"], "📥 Installing rkhunter...")

    run_command(["rkhunter", "--update"], "🌐 Updating rkhunter database...")
    run_command(["rkhunter", "--propupd", "--quiet"], "🧱 Creating baseline for file properties...")

    if confirm("Do you want to run an initial system check now?"):
        print("🔍 Running rkhunter check (press Enter to continue through prompts)...\n")
        subprocess.run(["rkhunter", "--check"])

    print("✅ rkhunter is installed and initialized. Schedule periodic checks via cron or systemd.")

if __name__ == "__main__":
    main()
