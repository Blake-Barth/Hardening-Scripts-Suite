#!/usr/bin/env python3

import os
import sys
import subprocess

# Hardcoded expected values (Lynis recommendations)
RECOMMENDED_SYSCTL = {
    "dev.tty.ldisc_autoload": 0,
    "fs.protected_fifos": 2,
    "fs.protected_hardlinks": 1,
    "fs.protected_regular": 2,
    "fs.protected_symlinks": 1,
    "fs.suid_dumpable": 0,
    "kernel.core_uses_pid": 1,
    "kernel.ctrl-alt-del": 0,
    "kernel.dmesg_restrict": 1,
    "kernel.kptr_restrict": 2,
    "kernel.modules_disabled": 1,
    "kernel.perf_event_paranoid": 2,
    "kernel.randomize_va_space": 2,
    "kernel.sysrq": 0,
    "kernel.unprivileged_bpf_disabled": 1,
    "kernel.yama.ptrace_scope": 1,
    "net.core.bpf_jit_harden": 2,
    "net.ipv4.conf.all.accept_redirects": 0,
    "net.ipv4.conf.all.accept_source_route": 0,
    "net.ipv4.conf.all.bootp_relay": 0,
    "net.ipv4.conf.all.forwarding": 0,
    "net.ipv4.conf.all.log_martians": 1,
    "net.ipv4.conf.all.mc_forwarding": 0,
    "net.ipv4.conf.all.proxy_arp": 0,
    "net.ipv4.conf.all.rp_filter": 1,
    "net.ipv4.conf.all.send_redirects": 0,
    "net.ipv4.conf.default.accept_redirects": 0,
    "net.ipv4.conf.default.accept_source_route": 0,
    "net.ipv4.conf.default.log_martians": 1,
    "net.ipv4.icmp_echo_ignore_broadcasts": 1,
    "net.ipv4.icmp_ignore_bogus_error_responses": 1,
    "net.ipv4.tcp_syncookies": 1,
    "net.ipv4.tcp_timestamps": 0,
    "net.ipv6.conf.all.accept_redirects": 0,
    "net.ipv6.conf.all.accept_source_route": 0,
    "net.ipv6.conf.default.accept_redirects": 0,
    "net.ipv6.conf.default.accept_source_route": 0
}

SYSCTL_CONF_FILE = "/etc/sysctl.d/99-lynis-recommendations.conf"

def confirm(prompt):
    return input(f"{prompt} (y/n): ").strip().lower() == "y"

def apply_sysctl(key, value):
    try:
        subprocess.run(["sysctl", f"{key}={value}"], check=True)
        print(f"✅ Set {key} = {value}")
        return f"{key} = {value}"
    except subprocess.CalledProcessError:
        print(f"❌ Failed to set {key}")
        return None

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root.")
        sys.exit(1)

    print("🔧 This script will walk through recommended sysctl settings from Lynis.")
    applied_lines = []

    for key, value in RECOMMENDED_SYSCTL.items():
        if confirm(f"Do you want to set `{key}` to `{value}`?"):
            result = apply_sysctl(key, value)
            if result:
                applied_lines.append(result)
        else:
            print(f"❎ Skipped {key}")

    if applied_lines and confirm("Do you want to save these changes to persist across reboots?"):
        try:
            with open(SYSCTL_CONF_FILE, "w") as f:
                f.write("# Lynis-recommended sysctl settings\n")
                for line in applied_lines:
                    f.write(line + "\n")
            print(f"💾 Settings saved to {SYSCTL_CONF_FILE}")
            subprocess.run(["sysctl", "--system"], check=True)
        except Exception as e:
            print(f"❌ Failed to save sysctl config: {e}")

if __name__ == "__main__":
    main()
