#!/usr/bin/env python3

import os
import sys
import subprocess

BLACKLIST_FILE = "/etc/modprobe.d/disable-usb.conf"
AVAILABLE_MODULES = {
    "usb-storage": "USB flash drive / external storage",
    "firewire-core": "FireWire device support",
    "bluetooth": "Bluetooth communication stack"
}

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def write_blacklist(modules):
    if not modules:
        print("❎ No modules selected. Nothing written.")
        return

    print(f"🔒 Writing blacklist to {BLACKLIST_FILE}...")
    with open(BLACKLIST_FILE, "w") as f:
        for mod in modules:
            f.write(f"install {mod} /bin/true\n")
            f.write(f"blacklist {mod}\n")
    print("✅ Blacklist written.")

def remove_loaded_modules(modules):
    for mod in modules:
        result = subprocess.run(["lsmod"], stdout=subprocess.PIPE, text=True)
        if mod.replace("-", "_") in result.stdout:
            print(f"⚠️  Module '{mod}' is currently loaded. Attempting to remove...")
            try:
                subprocess.run(["modprobe", "-r", mod], check=True)
                print(f"✅ Module '{mod}' removed from memory.")
            except subprocess.CalledProcessError:
                print(f"❌ Could not remove module '{mod}'. It may be in use.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    print("🛡️  This script helps disable unused kernel drivers for security.")

    selected_modules = []
    for mod, description in AVAILABLE_MODULES.items():
        if confirm(f"Disable {mod}? ({description})"):
            selected_modules.append(mod)

    if not selected_modules:
        print("❎ No drivers selected. Exiting.")
        return

    try:
        write_blacklist(selected_modules)

        if confirm("Do you want to remove these modules immediately if loaded?"):
            remove_loaded_modules(selected_modules)

        print("✅ Selected drivers have been disabled. Reboot recommended.")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
