#!/bin/bash

echo "───────────────────────────────────────────────────────────────"
echo " 🔥 Tool developed by Phantom-Code-CyberReign (Phantom Reign) "
echo " ⚠️ THIS TOOL IS FOR EDUCATIONAL PURPOSES ONLY!"
echo " 🚫 Unauthorized use for illegal activities is strictly prohibited."
echo " 🌐 Visit: github.com/Phantom-Code-CyberReign"
echo " 🏴 Based in Pakistan | Cybersecurity Research & Development"
echo "───────────────────────────────────────────────────────────────"


echo "[*] Killing interfering processes and enabling monitor mode..."
sudo airmon-ng check kill
sudo airmon-ng start wlan0

echo "[*] Running main Python tool script..."
sudo python3 wifi_phantom_trap.py
