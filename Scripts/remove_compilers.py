#!/usr/bin/env python3

import os
import sys
import subprocess

COMPILER_PACKAGES = ["gcc", "g++", "clang", "make"]

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🧼 Removing compilers: gcc, g++, clang, make")

    try:
        subprocess.run(["apt-get", "update"], check=True)
        subprocess.run(["apt-get", "remove", "--purge", "-y"] + COMPILER_PACKAGES, check=True)
        subprocess.run(["apt-get", "autoremove", "-y"], check=True)
        print("✅ Compilers removed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to remove compilers: {e}")

if __name__ == "__main__":
    main()
