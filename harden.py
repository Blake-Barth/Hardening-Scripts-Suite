import os
import sys

def check_admin():
    if os.geteuid() != 0:
        print("You need to run this script as root (sudo).")
        sys.exit(1)
    else:
        print("You are running as root.")

if __name__ == "main":
  check_admin()
