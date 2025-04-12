#!/usr/bin/env python3

import os
import sys
import subprocess

# List of protocols and their corresponding modules
PROTOCOLS = {
    "DCCP": "dccp",
    "SCTP": "sctp",
    "RDS": "rds",
    "TIPC": "tipc"
}

# Path to the blacklist file
BLACKLIST_FILE = "/etc/modprobe.d/blacklist.conf"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def check_module_loaded(module):
    """Check if a module is currently loaded."""
    result = subprocess.run(["lsmod"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return module in result.stdout.decode()

def remove_module(module):
    """Remove a loaded kernel module."""
    try:
        subprocess.run(["sudo", "modprobe", "-r", module], check=True)
        print(f"✅ {module} module removed.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error removing {module}: {e}")

def blacklist_module(module):
    """Add a module to the blacklist file to prevent it from loading."""
    try:
        with open(BLACKLIST_FILE, "a") as f:
            f.write(f"blacklist {module}\n")
        print(f"✅ {module} added to {BLACKLIST_FILE}.")
    except Exception as e:
        print(f"❌ Error blacklisting {module}: {e}")

def main():
    # Check if the script is run as root (for sudo access)
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo).")
        sys.exit(1)

    # Ask the user if they want to proceed
    print("⚠️ This script will remove and blacklist the following protocols:")
    for protocol in PROTOCOLS:
        print(f"  • {protocol}")

    if not confirm("Do you want to continue and disable these protocols?"):
        print("❎ Aborted by user.")
        return

    try:
        for protocol, module in PROTOCOLS.items():
            # Check if the module is loaded
            if check_module_loaded(module):
                if confirm(f"{protocol} module is loaded. Do you want to remove and blacklist it?"):
                    # Remove and blacklist the module
                    remove_module(module)
                    blacklist_module(module)
            else:
                print(f"{protocol} module is not loaded. Skipping...")

        print("✅ All selected modules processed successfully.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
