#!/usr/bin/env python3

import os
import subprocess
import time

# Define partition names and mount points
PARTITIONS = {
    '/home': '/dev/sdb1',
    '/tmp': '/dev/sdb2',
    '/var': '/dev/sdb3'
}

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == 'y'

def command_exists(command):
    return subprocess.run(['which', command], stdout=subprocess.PIPE).returncode == 0

def create_partition(device, start, size):
    if not confirm(f"Do you want to create a partition on {device}? This may overwrite existing data."):
        print("❎ Skipped partition creation.")
        return
    print(f"Creating partition on {device}...")
    try:
        subprocess.run(f"echo -e 'o\nn\np\n1\n{start}\n{size}\nw' | fdisk {device}", shell=True, check=True)
        print(f"✅ Partition created on {device}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating partition: {e}")
        exit(1)

def format_partition(partition):
    if not confirm(f"Do you want to format {partition} with ext4? All data will be erased."):
        print(f"❎ Skipped formatting {partition}.")
        return
    print(f"Formatting {partition} with ext4...")
    try:
        subprocess.run(f"mkfs.ext4 {partition}", shell=True, check=True)
        print(f"✅ {partition} formatted with ext4")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error formatting {partition}: {e}")
        exit(1)

def mount_partition(partition, mount_point):
    if not confirm(f"Do you want to mount {partition} at {mount_point}?"):
        print(f"❎ Skipped mounting {partition}.")
        return
    print(f"Mounting {partition} at {mount_point}...")
    try:
        if not os.path.exists(mount_point):
            os.makedirs(mount_point)
        subprocess.run(f"mount {partition} {mount_point}", shell=True, check=True)
        print(f"✅ {partition} mounted at {mount_point}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error mounting {partition} at {mount_point}: {e}")
        exit(1)

def update_fstab():
    if not confirm("Do you want to add these partitions to /etc/fstab for persistent mounting?"):
        print("❎ Skipped modifying /etc/fstab.")
        return
    print("Updating /etc/fstab...")
    try:
        with open("/etc/fstab", "a") as fstab:
            for mount_point, partition in PARTITIONS.items():
                fstab.write(f"{partition} {mount_point} ext4 defaults 0 2\n")
        print("✅ /etc/fstab updated.")
    except Exception as e:
        print(f"❌ Error updating /etc/fstab: {e}")
        exit(1)

def check_mounts():
    print("🔎 Checking if partitions are mounted...")
    for mount_point in PARTITIONS.keys():
        result = subprocess.run(f"mount | grep {mount_point}", shell=True, stdout=subprocess.PIPE)
        if result.stdout:
            print(f"✅ {mount_point} is mounted.")
        else:
            print(f"❌ {mount_point} is not mounted.")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        exit(1)

    if not (command_exists("fdisk") and command_exists("mkfs.ext4") and command_exists("mount")):
        print("❌ Required tools (fdisk, mkfs.ext4, mount) are missing.")
        exit(1)

    print("⚠️ This script makes permanent changes to disk partitions. Proceed with caution.")

    # Step 1: Create partition on base device
    create_partition("/dev/sdb", "2048", "10000")  # Example — adjust as needed

    # Step 2: Format partitions
    for mount_point, partition in PARTITIONS.items():
        format_partition(partition)

    # Step 3: Mount partitions
    for mount_point, partition in PARTITIONS.items():
        mount_partition(partition, mount_point)

    # Step 4: Update fstab
    update_fstab()

    # Step 5: Verify mounts
    check_mounts()

    print("📌 Please reboot the system to verify the partitions mount correctly.")
    time.sleep(3)

if __name__ == "__main__":
    main()
