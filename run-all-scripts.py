#!/usr/bin/env python3

import os
import sys
import subprocess

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Scripts")

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    if not os.path.isdir(SCRIPTS_DIR):
        print(f"❌ Directory '{SCRIPTS_DIR}' not found.")
        sys.exit(1)

    script_files = sorted(f for f in os.listdir(SCRIPTS_DIR)
                          if f.endswith(".py") and os.path.isfile(os.path.join(SCRIPTS_DIR, f)))

    if not script_files:
        print("⚠️  No Python scripts found in the Scripts directory.")
        return

    for script in script_files:
        full_path = os.path.join(SCRIPTS_DIR, script)
        print(f"\n🚀 Running: {script}")
        try:
            subprocess.run(["python3", full_path], check=True)
        except subprocess.CalledProcessError:
            print(f"❌ Error occurred while running {script}")

    # Prompt to reboot
    if confirm("\n🔄 All scripts complete. Would you like to reboot now?"):
        print("♻️ Rebooting...")
        subprocess.run(["reboot"])
    else:
        print("✅ Reboot skipped. Remember to restart manually if needed.")

if __name__ == "__main__":
    main()
