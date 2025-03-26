import os
import shutil
import sys
import subprocess
import re

def check_admin():
    if os.geteuid() != 0:
        print("❌ You need to run this script as root (sudo).")
        sys.exit(1)
    else:
        print("✅ You are running as root.")

def install_lynis_via_git(home_dir):
    repo_url = "https://github.com/CISOfy/lynis.git"
    install_path = os.path.join(home_dir, "lynis")

    if os.path.exists(install_path):
        print(f"📁 Directory {install_path} already exists. Skipping clone.")
    else:
        print(f"⬇️  Cloning Lynis into {install_path}...")
        subprocess.run(["git", "clone", repo_url, install_path], check=True)

    os.chdir(install_path)
    print(f"✅ Lynis is ready at: {install_path}")
    print(f"📂 Changed working directory to: {install_path}")

def check_lynis():
    lynis_path = shutil.which("lynis")

    if lynis_path:
        lynis_dir = os.path.dirname(lynis_path)
        print(f"✅ Lynis is installed system-wide at: {lynis_path}")
        os.chdir(lynis_dir)
        print(f"📂 Changed working directory to: {lynis_dir}")
        return

    # Check for local git install in ~/lynis
    home_dir = os.path.expanduser("~")
    local_lynis_path = os.path.join(home_dir, "lynis", "lynis")

    if os.path.isfile(local_lynis_path) and os.access(local_lynis_path, os.X_OK):
        print(f"✅ Lynis found in home directory at: {local_lynis_path}")
        os.chdir(os.path.dirname(local_lynis_path))
        print(f"📂 Changed working directory to: {os.getcwd()}")
        return

    # Not found — prompt to install
    print("⚠️  Lynis is not installed.")
    response = input("Would you like to clone Lynis from GitHub into your home directory? (y/n): ").strip().lower()
    if response == 'y':
        install_lynis_via_git(home_dir)
    else:
        print("❌ Lynis not installed. Exiting.")
        sys.exit(1)

def remove_ansi_sequences(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_lynis_and_save_output():
    lynis_executable = "./lynis" if os.path.isfile("./lynis") else "lynis"
    
    # Force output path to ~/lynis/lynis_report.txt
    home_dir = os.path.expanduser("~")
    report_dir = os.path.join(home_dir, "lynis")
    output_file = os.path.join(report_dir, "lynis_report.txt")

    os.makedirs(report_dir, exist_ok=True)

    print("\n⚠️  This system audit may take a minute or two to complete. Please be patient...\n")
    print(f"🚀 Running Lynis using: {lynis_executable}")

    try:
        result = subprocess.run(
            [lynis_executable, "audit", "system", "--no-colors", "--verbose"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=True
        )

        clean_output = remove_ansi_sequences(result.stdout)

        with open(output_file, "w") as f:
            f.write(clean_output)

        print(f"\n✅ Lynis audit complete.")
        print(f"📄 Output saved to: {output_file}")

    except subprocess.CalledProcessError as e:
        print("❌ Lynis failed to run.")
        print(f"Error: {e}")

# ===== Main Flow =====
check_admin()
check_lynis()
run_lynis_and_save_output()
