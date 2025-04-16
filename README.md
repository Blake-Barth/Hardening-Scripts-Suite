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
1. Password‑protect the GRUB bootloader
2. Display a pre‑login legal/notice banner
3. Harden SSH (disable root login, change port, enforce key‑based auth, etc.)
4. Keep the system fully patched and enable unattended security updates
5. Enforce strong password complexity and account‑lockout policies via PAM
6. Tighten kernel and network parameters through sysct
7. Disable non‑native binary support (binfmt_misc)
8. Disable core‑dump creation
9. Blacklist or remove unnecessary kernel modules/drivers (e.g., USB storage, FireWire, squashfs)
10. Disable legacy or insecure network services/protocols (rsh, telnet, talk, tftp, etc.)
11. Enable DNSSEC validation for secure name resolution
12. Enable process accounting to record command histories
13. Enable system activity logging with sysstat
14. Audit installed package versions for quick vulnerability checks
15. Install and configure rootkit detection with chkrootkit
16. Install and configure a UFW firewall with secure defaults
17. Remove development tools and compilers from production hosts
18. Lock down sudoer

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
