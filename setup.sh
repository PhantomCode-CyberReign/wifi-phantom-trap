#!/bin/bash
echo "[*] Killing interfering processes and enabling monitor mode..."
sudo airmon-ng check kill
sudo airmon-ng start wlan0

echo "[*] Running main Python tool script..."
sudo python3 wifi_phantom_trap.py
