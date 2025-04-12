#!/usr/bin/env python3

import os
import sys
import subprocess

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def run(command, silent=False):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=silent)
        if not silent:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        return False

def install_chkrootkit():
    print("📦 Installing chkrootkit...")
    run("apt update")
    run("apt install -y chkrootkit")
    print("✅ chkrootkit installed.")

def run_chkrootkit():
    print("🔍 Running chkrootkit scan...")
    run("chkrootkit")

def setup_cron():
    print("📅 Setting up daily chkrootkit scan via cron...")
    cron_line = "@daily /usr/sbin/chkrootkit > /var/log/chkrootkit.log 2>&1"
    try:
        existing = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
        if cron_line in existing.stdout:
            print("ℹ️ Daily chkrootkit cron job already set.")
            return
    except subprocess.CalledProcessError:
        existing = ""

    updated_cron = existing.stdout + f"\n{cron_line}\n" if existing.stdout else f"{cron_line}\n"
    subprocess.run(f"(echo \"{updated_cron.strip()}\") | crontab -", shell=True, check=True)
    print("✅ Daily chkrootkit cron job added (logs to /var/log/chkrootkit.log).")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🔐 This script will install and configure chkrootkit for malware/rootkit detection.")

    if confirm("Do you want to install chkrootkit?"):
        install_chkrootkit()
    else:
        print("❎ Skipping installation.")
        return

    if confirm("Do you want to run chkrootkit now?"):
        run_chkrootkit()

    if confirm("Do you want to configure chkrootkit to run daily via cron?"):
        setup_cron()

if __name__ == "__main__":
    main()
