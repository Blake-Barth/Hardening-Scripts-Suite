#!/usr/bin/env python3

import os
import sys
import subprocess

CONFIG_PATH = "/etc/systemd/resolved.conf"
DNSSEC_LINE = "DNSSEC=yes"
SECTION_HEADER = "[Resolve]"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def read_config_lines():
    if not os.path.exists(CONFIG_PATH):
        print("❌ systemd-resolved config not found.")
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return f.readlines()

def write_config_lines(lines):
    with open(CONFIG_PATH, "w") as f:
        f.writelines(lines)

def ensure_dnssec_enabled():
    lines = read_config_lines()
    updated = False
    in_resolve_section = False
    new_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("[") and stripped.lower() != "[resolve]":
            in_resolve_section = False

        if stripped.lower() == "[resolve]":
            in_resolve_section = True
            new_lines.append(line)
            continue

        if in_resolve_section and stripped.startswith("DNSSEC="):
            new_lines.append("DNSSEC=yes\n")
            updated = True
            continue

        new_lines.append(line)

    # If [Resolve] section not present
    if not any("[Resolve]" in line for line in lines):
        new_lines.append("\n[Resolve]\n")
        new_lines.append("DNSSEC=yes\n")
        updated = True

    # If [Resolve] present but no DNSSEC line
    elif in_resolve_section and not any("DNSSEC=" in l for l in new_lines if "[Resolve]" in l or l.strip().startswith("DNSSEC=")):
        new_lines.append("DNSSEC=yes\n")
        updated = True

    if updated:
        write_config_lines(new_lines)
        print("✅ DNSSEC setting applied to resolved.conf")
    else:
        print("ℹ️ DNSSEC already set to 'yes'")

def restart_resolved():
    print("🔁 Restarting systemd-resolved...")
    try:
        subprocess.run(["systemctl", "restart", "systemd-resolved"], check=True)
        print("✅ systemd-resolved restarted.")
    except subprocess.CalledProcessError:
        print("❌ Failed to restart systemd-resolved.")

def show_dnssec_status():
    print("\n📊 Current DNSSEC Status:")
    subprocess.run(["resolvectl", "status"])

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🔐 This script enables DNSSEC support via systemd-resolved.")

    if not confirm("Do you want to enable DNSSEC in systemd-resolved?"):
        print("❎ Aborted by user.")
        return

    ensure_dnssec_enabled()
    restart_resolved()
    show_dnssec_status()

if __name__ == "__main__":
    main()
