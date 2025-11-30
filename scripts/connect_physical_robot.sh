#!/bin/bash

ADB="/home/linda/Android/Sdk/platform-tools/adb"

# Ask for IP using GUI
IP=$(zenity --entry --title="Connect to Pepper" --text="Enter Robot IP Address (e.g. 192.168.1.X):" --entry-text="192.168.")

if [ -z "$IP" ]; then
    echo "Canceled."
    exit 1
fi

# Connect
echo "Attempting to connect to $IP..."
OUTPUT=$($ADB connect $IP)
echo "ADB Output: $OUTPUT"

if echo "$OUTPUT" | grep -q "connected"; then
    zenity --info --text="Successfully connected to Pepper at $IP"
else
    zenity --error --text="Failed to connect:\n$OUTPUT"
fi
