#!/usr/bin/env python3

import os
import sys
import shutil
import re

SSHD_CONFIG = "/etc/ssh/sshd_config"
BACKUP_PATH = SSHD_CONFIG + ".bak"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def backup_file():
    if not os.path.exists(BACKUP_PATH):
        shutil.copy2(SSHD_CONFIG, BACKUP_PATH)
        print(f"🗂️  Backed up {SSHD_CONFIG} to {BACKUP_PATH}")

def set_or_replace(config_lines, key, value):
    pattern = re.compile(rf"^\s*{re.escape(key)}\s+")
    for i, line in enumerate(config_lines):
        if pattern.match(line):
            config_lines[i] = f"{key} {value}\n"
            return config_lines
    config_lines.append(f"{key} {value}\n")
    return config_lines

def update_sshd_config(changes):
    backup_file()

    with open(SSHD_CONFIG, "r") as f:
        lines = f.readlines()

    for key, value in changes.items():
        lines = set_or_replace(lines, key, value)

    with open(SSHD_CONFIG, "w") as f:
        f.writelines(lines)

    print("✅ SSH config updated. You should restart sshd: `systemctl restart sshd`")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🔐 This script will interactively harden your SSH server configuration.\n")

    changes = {}

    # 1. LogLevel
    if confirm("Set SSH log level to 'VERBOSE'? (for detailed logging)"):
        changes["LogLevel"] = "VERBOSE"

    # 2. MaxAuthTries
    if confirm("Limit MaxAuthTries to 3? (Prevents brute-force login attempts)"):
        changes["MaxAuthTries"] = "3"

    # 3. MaxSessions
    if confirm("Limit MaxSessions to 2? (Limits concurrent connections)"):
        changes["MaxSessions"] = "2"

    # 4. PermitRootLogin
    print("Configure root SSH login:")
    print("  - yes (⚠️ insecure)")
    print("  - no (recommended)")
    print("  - prohibit-password (allow only key-based)")
    print("  - without-password (legacy key-based)")
    option = input("Enter value for PermitRootLogin: ").strip()
    if option in ["yes", "no", "prohibit-password", "without-password"]:
        changes["PermitRootLogin"] = option

    # 5. Port
    if confirm("Do you want to change the SSH port from 22 to 2048?"):
        changes["Port"] = "2048"

    # 6. TCPKeepAlive
    if confirm("Disable TCPKeepAlive? (Set to 'no' to reduce exposure)"):
        changes["TCPKeepAlive"] = "no"

    # 7. X11Forwarding
    if confirm("Disable X11Forwarding? (recommended unless needed)"):
        changes["X11Forwarding"] = "no"

    # 8. AllowTcpForwarding
    if confirm("Disable AllowTcpForwarding? (prevents port forwarding abuse)"):
        changes["AllowTcpForwarding"] = "no"

    if changes:
        update_sshd_config(changes)

        if confirm("Would you like to restart the SSH service now to apply changes?"):
            print("🧪 Testing SSH configuration with `sshd -t`...")
            try:
                subprocess.run(["sshd", "-t"], check=True)
                print("✅ SSH configuration is valid.")

                try:
                    subprocess.run(["systemctl", "restart", "ssh"], check=True)
                    print("🔁 SSH service restarted using 'ssh'.")
                except subprocess.CalledProcessError:
                    print("⚠️  Failed to restart using 'ssh'. Trying 'sshd'...")
                    try:
                        subprocess.run(["systemctl", "restart", "sshd"], check=True)
                        print("🔁 SSH service restarted using 'sshd'.")
                    except subprocess.CalledProcessError:
                        print("❌ Failed to restart SSH with both 'ssh' and 'sshd'. Please restart manually.")

            except subprocess.CalledProcessError:
                print("❌ SSH configuration test failed! Not restarting service.")
                print("⚠️  Please fix the configuration manually and test with `sshd -t`.")
        else:
            print("⚠️  Remember to restart SSH for changes to take effect.")
    else:
        print("❎ No changes selected. SSH config left untouched.")

if __name__ == "__main__":
    main()
