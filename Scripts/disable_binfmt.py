#!/usr/bin/env python3

import os
import subprocess
import sys

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def is_binfmt_mounted():
    try:
        with open("/proc/mounts", "r") as f:
            return any("binfmt_misc" in line for line in f)
    except Exception:
        return False

def unmount_binfmt():
    print("🔌 Unmounting /proc/sys/fs/binfmt_misc...")
    try:
        subprocess.run(["umount", "/proc/sys/fs/binfmt_misc"], check=True)
        print("✅ binfmt_misc unmounted.")
    except subprocess.CalledProcessError:
        print("⚠️ Could not unmount binfmt_misc. It may not be mounted or in use.")

def disable_systemd_binfmt():
    print("🔧 Disabling systemd-binfmt.service...")
    try:
        subprocess.run(["systemctl", "stop", "systemd-binfmt.service"], check=True)
        subprocess.run(["systemctl", "mask", "systemd-binfmt.service"], check=True)
        print("✅ systemd-binfmt.service stopped and masked.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to disable systemd-binfmt.service: {e}")

def show_status():
    print("\n📊 Current binfmt_misc status:")
    if os.path.exists("/proc/sys/fs/binfmt_misc/status"):
        subprocess.run(["cat", "/proc/sys/fs/binfmt_misc/status"])
    else:
        print("ℹ️ binfmt_misc is not mounted or already disabled.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🔐 This script disables non-native binary execution (binfmt_misc).")

    if not confirm("Proceed to disable binfmt_misc and mask systemd-binfmt?"):
        print("❎ Aborted by user.")
        return

    if is_binfmt_mounted():
        unmount_binfmt()
    else:
        print("ℹ️ binfmt_misc is not currently mounted.")

    disable_systemd_binfmt()
    show_status()

    print("\n♻️ Reboot recommended to fully apply the changes.")

if __name__ == "__main__":
    main()
