#!/usr/bin/env python3

import os
import sys
import subprocess

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def command_exists(command):
    return subprocess.run(['which', command], stdout=subprocess.PIPE).returncode == 0

def install_aide():
    print("📦 Installing AIDE...")
    try:
        subprocess.run(["apt", "update"], check=True)
        subprocess.run(["apt", "install", "aide", "-y"], check=True)
        print("✅ AIDE installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing AIDE: {e}")
        sys.exit(1)

def initialize_aide():
    print("📄 Initializing AIDE database...")
    try:
        subprocess.run(["aideinit"], check=True)
        subprocess.run(["mv", "/var/lib/aide/aide.db.new", "/var/lib/aide/aide.db"], check=True)
        print("✅ AIDE database initialized.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error initializing AIDE: {e}")
        sys.exit(1)

def configure_aide():
    print("🛠️ Configuring AIDE settings...")
    aide_conf_file = "/etc/aide/aide.conf"
    banner = """
# Monitoring sensitive files and directories
/etc    FIPOS
/var/log FIPOS
/var/www FIPOS
/etc/passwd FIPOS
/etc/shadow FIPOS
"""
    try:
        if not os.path.exists(aide_conf_file):
            print(f"❌ {aide_conf_file} does not exist.")
            sys.exit(1)
        with open(aide_conf_file, "a") as f:
            f.write(banner)
        print("✅ AIDE configuration updated.")
    except Exception as e:
        print(f"❌ Error configuring AIDE: {e}")
        sys.exit(1)

def run_aide_check():
    print("🔍 Running AIDE integrity check...")
    try:
        subprocess.run(["aide", "--check"], check=True)
        print("✅ AIDE integrity check completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ AIDE check failed: {e}")
        sys.exit(1)

def setup_cron():
    print("⏰ Setting up cron job to run AIDE daily...")
    cron_job = "0 0 * * * /usr/bin/aide --check\n"
    try:
        if not command_exists('crontab'):
            print("❌ Cron is not installed.")
            sys.exit(1)
        subprocess.run(f"(echo \"{cron_job}\") | crontab -", shell=True, check=True)
        print("✅ Cron job set up to run AIDE daily.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up cron job: {e}")
        sys.exit(1)

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🔐 AIDE (Advanced Intrusion Detection Environment) Setup")

    if not command_exists("aide"):
        if confirm("AIDE is not installed. Install it?"):
            install_aide()
        else:
            print("❎ Skipped AIDE installation.")
            return
    else:
        print("✅ AIDE is already installed.")

    if confirm("Initialize the AIDE database?"):
        initialize_aide()

    if confirm("Update AIDE config to monitor common sensitive files?"):
        configure_aide()

    if confirm("Run AIDE check now?"):
        run_aide_check()

    if confirm("Set up a daily cron job to run AIDE?"):
        setup_cron()

if __name__ == "__main__":
    main()
