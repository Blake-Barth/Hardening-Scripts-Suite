Linux System Hardening Scripts
==============================

This project is a collection of interactive Python scripts designed to harden and secure a Linux system, especially for production 
or security-sensitive environments. Each script handles a specific security control or configuration task and prompts the user before making any changes.

Key Features:
-------------
✔️ Per-script confirmations to avoid accidental changes  
✔️ Compatible with Debian/Ubuntu-based systems  
✔️ Designed to optimize Lynis audit score on Unbuntu machine from Linode

Included Hardening Tasks:
-------------------------
1. Configure and protect GRUB with a password
2. Enforce secure SSH configuration (e.g., disable root login, change port)
3. Disable non-native binary support (binfmt_misc)
4. Harden sysctl settings for kernel/network security
5. Remove or restrict compilers to prevent local exploit compilation
6. Enable and configure AIDE (Advanced Intrusion Detection Environment)
7. Install chkrootkit for rootkit detection
8. Install and configure UFW firewall
9. Install Chroot or other malware detection tools (optional)

How to Use:
-----------
1. Clone or download the scripts into a secure folder:
   $ git clone [repo-url] hardening-scripts

2. Enter the folder:
   $ cd Linux-Hardening Suite

3. Run scripts individually as root:
   $ cd Scripts
   $ sudo python3 001-GRUB-password.py
   $ sudo python3 002-SSH-harden.py
   ...
   OR run all at once:
   $ sudo python3 run_all_scripts.py

5. Reboot after major changes (e.g., GRUB, SSH, partitions).

Recommendations:
----------------
- Review each script before use to understand what changes it makes
- Run on a test VM or staging server before production deployment
- Keep backups!
  
Disclaimer:
-----------
These Scripts were made for a hardening project and are for demonstrative 

Author:
-------
Blake Barth (FSU)
