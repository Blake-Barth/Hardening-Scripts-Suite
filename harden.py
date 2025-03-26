import os
import shutil
import sys
import subprocess

def check_admin():
    if os.geteuid() != 0:
        print("You need to run this script as root (sudo).")
        sys.exit(1)
    else:
        print("You are running as root.")

def install_lynis_via_git(home_dir):
    repo_url = "https://github.com/CISOfy/lynis.git"
    install_path = os.path.join(home_dir, "lynis")

    if os.path.exists(install_path):
        print(f"Directory {install_path} already exists. Skipping clone.")
    else:
        print(f"Cloning Lynis into {install_path}...")
        subprocess.run(["git", "clone", repo_url, install_path], check=True)

    os.chdir(install_path)
    print(f"Lynis installed to: {install_path}")
    print(f"Changed working directory to: {install_path}")

def check_lynis():
    lynis_path = shutil.which("lynis")

    if lynis_path:
        lynis_dir = os.path.dirname(lynis_path)
        print(f"Lynis is installed at: {lynis_path}")
        os.chdir(lynis_dir)
        print(f"Changed working directory to: {lynis_dir}")
    else:
        home_dir = os.path.expanduser("~")
        print("Lynis is not installed.")
        response = input("Would you like to clone Lynis from GitHub into your home directory? (y/n): ").strip().lower()
        if response == 'y':
            install_lynis_via_git(home_dir)
        else:
            print("Lynis not installed. Exiting.")
            sys.exit(1)

# Main execution
check_admin()
check_lynis()
