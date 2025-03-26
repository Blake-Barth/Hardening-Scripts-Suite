import os
import shutil
import sys
import subprocess
import re
import glob
from datetime import datetime

def log_action(message, log_file=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_log = os.path.join(script_dir, "hardening_log.txt")
    log_path = log_file or default_log

    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    full_message = f"{timestamp} {message}\n"

    try:
        with open(log_path, "a") as f:
            f.write(full_message)
    except Exception as e:
        print(f"⚠️  Failed to write to log: {e}")

def check_admin():
    if os.geteuid() != 0:
        print("❌ You need to run this script as root (sudo).")
        sys.exit(1)
    else:
        print("✅ You are running as root.")
        log_action("Confirmed script is running with root privileges.")

def install_lynis_via_git(home_dir):
    repo_url = "https://github.com/CISOfy/lynis.git"
    install_path = os.path.join(home_dir, "lynis")

    if os.path.exists(install_path):
        print(f"📁 Directory {install_path} already exists. Skipping clone.")
        log_action(f"Skipped cloning Lynis, already exists at {install_path}")
    else:
        print(f"⬇️  Cloning Lynis into {install_path}...")
        subprocess.run(["git", "clone", repo_url, install_path], check=True)
        log_action(f"Cloned Lynis from GitHub into {install_path}")

    os.chdir(install_path)
    print(f"✅ Lynis is ready at: {install_path}")
    print(f"📂 Changed working directory to: {install_path}")
    log_action(f"Changed working directory to: {install_path}")

def check_lynis():
    lynis_path = shutil.which("lynis")

    if lynis_path:
        lynis_dir = os.path.dirname(lynis_path)
        print(f"✅ Lynis is installed system-wide at: {lynis_path}")
        os.chdir(lynis_dir)
        print(f"📂 Changed working directory to: {lynis_dir}")
        log_action(f"Using system-installed Lynis at {lynis_path}")
        return

    home_dir = os.path.expanduser("~")
    local_lynis_path = os.path.join(home_dir, "lynis", "lynis")

    if os.path.isfile(local_lynis_path) and os.access(local_lynis_path, os.X_OK):
        print(f"✅ Lynis found in home directory at: {local_lynis_path}")
        os.chdir(os.path.dirname(local_lynis_path))
        print(f"📂 Changed working directory to: {os.getcwd()}")
        log_action(f"Using locally installed Lynis at {local_lynis_path}")
        return

    print("⚠️  Lynis is not installed.")
    response = input("Would you like to clone Lynis from GitHub into your home directory? (y/n): ").strip().lower()
    if response == 'y':
        install_lynis_via_git(home_dir)
    else:
        print("❌ Lynis not installed. Exiting.")
        log_action("User declined to install Lynis. Exiting.")
        sys.exit(1)

def remove_ansi_sequences(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def print_hardening_score(report_path):
    try:
        with open(report_path, "r") as f:
            for line in f:
                if "Hardening index" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        score = parts[1].strip().split()[0]
                        print(f"\n🔐 Lynis Hardening Index: {score}/100")
                        log_action(f"Hardening Index reported: {score}/100")
                        return
        print("\n⚠️  Could not find hardening score in report.")
        log_action("Could not find hardening score in report.")
    except Exception as e:
        print(f"\n❌ Failed to read report: {e}")
        log_action(f"Error reading report for hardening index: {e}")

def parse_sysctl_differences(report_path):
    diffs = {}
    # Accept optional leading dash, handle extra space, skip multi-values
    pattern = re.compile(r'^\-?\s*([\w\.\-]+)\s+\(exp:\s*([^\)]+)\)\s+\[\s*DIFFERENT\s*\]', re.IGNORECASE)

    with open(report_path, 'r') as file:
        for line in file:
            match = pattern.search(line.strip())
            if match:
                key, expected_value = match.groups()
                expected_value = expected_value.strip()

                # Skip if multiple expected values (comma, space, or 'or')
                if ',' in expected_value or ' ' in expected_value or 'or' in expected_value:
                    log_action(f"Skipping ambiguous expected value for {key}: '{expected_value}'")
                    continue

                diffs[key] = expected_value
    return diffs

def apply_sysctl_fixes(settings, conf_path="/etc/sysctl.d/99-lynis-hardening.conf"):
    log_action("Applying sysctl hardening values from Lynis scan.")

    to_write = {}

    for key, desired in settings.items():
        try:
            result = subprocess.run(["sysctl", "-n", key], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            current = result.stdout.strip()

            if current != desired:
                to_write[key] = desired
                log_action(f"Will change {key}: current={current}, expected={desired}")
            else:
                log_action(f"Skipping {key}: already set to {current}")
        except Exception as e:
            log_action(f"Failed to check {key}: {e}")

    if not to_write:
        log_action("All sysctl values already correct. No changes made.")
        return

    try:
        with open(conf_path, "a") as f:
            for key, value in to_write.items():
                f.write(f"{key} = {value}\n")
                log_action(f"Persisted sysctl: {key} = {value} in {conf_path}")
    except Exception as e:
        log_action(f"ERROR writing to {conf_path}: {e}")
        return

    try:
        subprocess.run(["sysctl", "--system"], check=True)
        log_action("Reloaded sysctl settings using sysctl --system.")
    except subprocess.CalledProcessError as e:
        log_action(f"ERROR reloading sysctl settings: {e}")

def run_lynis_and_save_output():
    lynis_executable = "./lynis" if os.path.isfile("./lynis") else "lynis"

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "lynis_report.txt")

    # ===== TEMPORARY BLOCK FOR PERSONAL DEV USE =====
    # ⚠️ REMOVE THIS BLOCK LATER IF USED IN PROD
    existing_reports = glob.glob(os.path.join(script_dir, "report_*.txt")) + \
                       ([output_file] if os.path.exists(output_file) else [])

    if existing_reports:
        print("📝 Existing Lynis report(s) found:")
        for path in existing_reports:
            print(f" - {os.path.basename(path)}")
        resp = input("Would you like to re-run Lynis anyway? (y/n): ").strip().lower()
        if resp != 'y':
            print("✅ Skipping Lynis scan.")
            log_action("Skipped Lynis scan due to existing report.")
            
            sysctl_diffs = parse_sysctl_differences(output_file)
            if sysctl_diffs:
                apply_sysctl_fixes(sysctl_diffs)
            else:
                print("✅ No sysctl differences found to fix.")
                log_action("No sysctl differences found in existing report.")
            return
    # ===== END TEMPORARY BLOCK =====

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
        log_action(f"Lynis audit complete. Report saved to: {output_file}")

        print_hardening_score(output_file)

        sysctl_diffs = parse_sysctl_differences(output_file)
        if sysctl_diffs:
            apply_sysctl_fixes(sysctl_diffs)
        else:
            print("✅ No sysctl differences found to fix.")
            log_action("No sysctl differences found in scan.")

    except subprocess.CalledProcessError as e:
        print("❌ Lynis failed to run.")
        print(f"Error: {e}")
        log_action(f"Lynis failed to run: {e}")

# ===== Main Flow =====
check_admin()
check_lynis()
run_lynis_and_save_output()
