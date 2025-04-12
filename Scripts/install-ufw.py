#!/usr/bin/env python3

import os
import sys
import subprocess

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def run_command(command, description=None):
    if description:
        print(description)
    try:
        subprocess.run(command, check=True)
        print(f"✅ {' '.join(command)} completed.")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to run: {' '.join(command)}")

def install_ufw():
    run_command(["apt-get", "update"], "📦 Updating package lists...")
    run_command(["apt-get", "install", "-y", "ufw"], "🔧 Installing UFW...")

def configure_ufw():
    print("🔧 Setting default UFW policies...")
    run_command(["ufw", "default", "deny", "incoming"])
    run_command(["ufw", "default", "allow", "outgoing"])

    # Custom SSH port input
    ssh_port = input("Enter your custom SSH port (leave blank to skip): ").strip()
    if ssh_port.isdigit():
        run_command(["ufw", "allow", f"{ssh_port}/tcp"], f"🔐 Allowing SSH on port {ssh_port}...")
    elif ssh_port:
        print("⚠️  Invalid port provided. Skipping SSH rule.")

    if confirm("Allow HTTP (port 80)?"):
        run_command(["ufw", "allow", "http"])

    if confirm("Allow HTTPS (port 443)?"):
        run_command(["ufw", "allow", "https"])

    if confirm("Enable UFW now?"):
        run_command(["ufw", "enable"], "🔥 Enabling UFW...")
    else:
        print("⚠️  UFW not enabled. Your rules are configured but inactive.")

    print("\n📊 Final UFW Status:")
    subprocess.run(["ufw", "status", "verbose"])

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🛡️  This script installs and configures UFW (Uncomplicated Firewall).")
    print("🔐 SSH port: You will be prompted to enter the custom SSH port manually.")

    if not confirm("Do you want to install and configure UFW?"):
        print("❎ Aborted by user.")
        return

    install_ufw()
    configure_ufw()

if __name__ == "__main__":
    main()
