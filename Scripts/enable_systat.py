#!/usr/bin/env python3

import os
import sys
import subprocess

SYSSTAT_CONF = "/etc/default/sysstat"

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

def install_sysstat():
    run_command(["apt-get", "update"], "📦 Updating package lists...")
    run_command(["apt-get", "install", "-y", "sysstat"], "🔧 Installing sysstat...")

def enable_sysstat():
    print("🛠️  Enabling sysstat logging in /etc/default/sysstat...")
    try:
        lines = []
        with open(SYSSTAT_CONF, "r") as f:
            lines = f.readlines()

        with open(SYSSTAT_CONF, "w") as f:
            for line in lines:
                if line.strip().startswith("ENABLED="):
                    f.write("ENABLED=\"true\"\n")
                else:
                    f.write(line)
        print("✅ sysstat enabled.")
    except Exception as e:
        print(f"❌ Failed to modify {SYSSTAT_CONF}: {e}")
        sys.exit(1)

def restart_services():
    print("🔄 Restarting sysstat collection service...")
    try:
        subprocess.run(["systemctl", "restart", "sysstat"], check=True)
        print("✅ sysstat service restarted.")
    except subprocess.CalledProcessError:
        print("⚠️  systemd restart failed, trying cron restart (older systems)...")
        subprocess.run(["systemctl", "restart", "cron"], check=False)

def verify_sar():
    print("📊 Verifying `sar` output...")
    try:
        subprocess.run(["sar", "-u", "1", "1"], check=True)
        print("✅ sar is collecting system activity.")
    except subprocess.CalledProcessError:
        print("⚠️  sar did not return expected output. It may need more time to collect data.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("📈 This script enables sysstat (sar/iostat) for system activity logging.")

    if not confirm("Do you want to install and enable sysstat?"):
        print("❎ Aborted by user.")
        return

    install_sysstat()
    enable_sysstat()
    restart_services()
    verify_sar()

if __name__ == "__main__":
    main()
