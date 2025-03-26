import os
import shutil
import sys
import subprocess
import urllib.request
import tarfile


def check_admin():
    if os.geteuid() != 0:
        print("You need to run this script as root (sudo).")
        sys.exit(1)
def download_and_install_lynis(home_dir):
    lynis_url = "https://downloads.cisofy.com/lynis/lynis-3.0.9.tar.gz"  # or latest version
    download_path = os.path.join(home_dir, "lynis.tar.gz")
    extract_path = os.path.join(home_dir, "lynis")

    print("Downloading Lynis...")
    urllib.request.urlretrieve(lynis_url, download_path)

    print("Extracting Lynis...")
    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(path=home_dir)

    # Rename extracted folder (e.g., lynis-3.0.9 → lynis)
    for item in os.listdir(home_dir):
        if item.startswith("lynis-") and os.path.isdir(os.path.join(home_dir, item)):
            os.rename(os.path.join(home_dir, item), extract_path)
            break

    os.remove(download_path)
    os.chdir(extract_path)
    print(f"Lynis installed to: {extract_path}")
    print(f"Changed working directory to: {extract_path}")

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
        response = input("Would you like to install Lynis in your home directory? (y/n): ").strip().lower()
        if response == 'y':
            download_and_install_lynis(home_dir)
        else:
            print("Lynis not installed. Exiting.")
            sys.exit(1)

if __name__ == "main":
  check_admin()
  check_lynis()
