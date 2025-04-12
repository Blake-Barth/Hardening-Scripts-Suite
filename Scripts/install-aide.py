#!/usr/bin/env python3

import os
import sys
import subprocess
import time

# Function to check if a command exists
def command_exists(command):
    return subprocess.run(['which', command], stdout=subprocess.PIPE).returncode == 0

# Install AIDE if not installed
def install_aide():
    print("Installing AIDE...")
    try:
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "aide", "-y"], check=True)
        print("✅ AIDE installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing AIDE: {e}")
        sys.exit(1)

# Initialize AIDE database
def initialize_aide():
    print("Initializing AIDE database...")
    try:
        subprocess.run(["sudo", "aideinit"], check=True)
        # Move the new database to the default location
        subprocess.run(["sudo", "mv", "/var/lib/aide/aide.db.new", "/var/lib/aide/aide.db"], check=True)
        print("✅ AIDE database initialized.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error initializing AIDE: {e}")
        sys.exit(1)

# Configure AIDE (edit /etc/aide/aide.conf)
def configure_aide():
    print("Configuring AIDE settings...")
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
        # Check if file exists, if not create it
        if not os.path.exists(aide_conf_file):
            print(f"❌ {aide_conf_file} does not exist.")
            sys.exit(1)
        
        with open(aide_conf_file, "a") as f:
            f.write(banner)
        
        print("✅ AIDE configuration updated.")
    except Exception as e:
        print(f"❌ Error configuring AIDE: {e}")
        sys.exit(1)

# Run AIDE integrity check
def run_aide_check():
    print("Running AIDE integrity check...")
    try:
        subprocess.run(["sudo", "aide", "--check"], check=True)
        print("✅ AIDE integrity check completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ AIDE check failed: {e}")
        sys.exit(1)

# Set up a cron job to run AIDE check daily
def setup_cron():
    print("Setting up cron job to run AIDE daily...")
    cron_job = "0 0 * * * /usr/bin/aide --check\n"
    try:
        # Check if cron is installed
        if not command_exists('crontab'):
            print("❌ Cron is not installed.")
            sys.exit(1)
        
        # Add the cron job
        subprocess.run(f"(echo \"{cron_job}\") | sudo crontab -", shell=True, check=True)
        print("✅ Cron job set up to run AIDE daily.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error setting up cron job: {e}")
        sys.exit(1)

def main():
    # Check if the script is run as root (for sudo access)
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)
    
    # Step 1: Install AIDE if not already installed
    if not command_exists("aide"):
        install_aide()
    else:
        print("AIDE is already installed.")

    # Step 2: Initialize AIDE database
    initialize_aide()

    # Step 3: Configure AIDE to monitor sensitive files
    configure_aide()

    # Step 4: Run the AIDE integrity check
    run_aide_check()

    # Step 5: Set up a cron job to run the AIDE check daily
    setup_cron()

if __name__ == "__main__":
    main()
