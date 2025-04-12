import os
import subprocess
import time

# Define partition names and mount points
PARTITIONS = {
    '/home': '/dev/sdb1',  # Example partition; replace with actual device
    '/tmp': '/dev/sdb2',   # Example partition; replace with actual device
    '/var': '/dev/sdb3'    # Example partition; replace with actual device
}

# Function to check if a command exists
def command_exists(command):
    return subprocess.run(['which', command], stdout=subprocess.PIPE).returncode == 0

# Function to create a partition using fdisk (very basic)
def create_partition(device, start, size):
    print(f"Creating partition on {device}...")
    try:
        subprocess.run(f"echo -e 'o\nn\np\n1\n{start}\n{size}\nw' | sudo fdisk {device}", shell=True, check=True)
        print(f"✅ Partition created on {device}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating partition: {e}")
        exit(1)

# Function to format the partition with ext4
def format_partition(partition):
    print(f"Formatting {partition} with ext4...")
    try:
        subprocess.run(f"sudo mkfs.ext4 {partition}", shell=True, check=True)
        print(f"✅ {partition} formatted with ext4")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error formatting {partition}: {e}")
        exit(1)

# Function to mount the partition
def mount_partition(partition, mount_point):
    print(f"Mounting {partition} at {mount_point}...")
    try:
        if not os.path.exists(mount_point):
            os.makedirs(mount_point)
        subprocess.run(f"sudo mount {partition} {mount_point}", shell=True, check=True)
        print(f"✅ {partition} mounted at {mount_point}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error mounting {partition} at {mount_point}: {e}")
        exit(1)

# Function to modify /etc/fstab for permanent mounting
def update_fstab():
    print("Updating /etc/fstab to ensure the partitions mount on boot...")
    try:
        with open("/etc/fstab", "a") as fstab:
            for mount_point, partition in PARTITIONS.items():
                fstab.write(f"{partition} {mount_point} ext4 defaults 0 2\n")
        print("✅ /etc/fstab updated")
    except Exception as e:
        print(f"❌ Error updating /etc/fstab: {e}")
        exit(1)

# Function to check if partitions are already mounted
def check_mounts():
    print("Checking if partitions are already mounted...")
    for mount_point in PARTITIONS.keys():
        result = subprocess.run(f"mount | grep {mount_point}", shell=True, stdout=subprocess.PIPE)
        if result.stdout:
            print(f"✅ {mount_point} is already mounted.")
        else:
            print(f"❌ {mount_point} is not mounted yet.")

def main():
    # Ensure the required tools (fdisk, mkfs, mount) are available
    if not command_exists("fdisk") or not command_exists("mkfs.ext4") or not command_exists("mount"):
        print("❌ Required tools (fdisk, mkfs.ext4, mount) are not available. Please install them first.")
        exit(1)

    # Step 1: Create partitions (skip if already created)
    print("This will create partitions on the disk. Make sure you have backups!")
    create_partition("/dev/sdb", "2048", "10000")  # Adjust as necessary (replace /dev/sdb)

    # Step 2: Format partitions with ext4
    for mount_point, partition in PARTITIONS.items():
        format_partition(partition)

    # Step 3: Mount partitions
    for mount_point, partition in PARTITIONS.items():
        mount_partition(partition, mount_point)

    # Step 4: Update fstab to mount on boot
    update_fstab()

    # Step 5: Check if the partitions are mounted correctly
    check_mounts()

    print("⚠️ Please reboot your system to ensure the changes take effect.")
    time.sleep(5)

if __name__ == "__main__":
    main()
