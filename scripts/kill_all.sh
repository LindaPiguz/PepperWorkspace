#!/bin/bash

# kill_all.sh
# Force kills all emulator and ADB processes to reset the environment.

echo "Killing Emulator processes..."
pkill -9 -f "emulator"
pkill -9 -f "qemu-system"

echo "Killing ADB server..."
adb kill-server
adb disconnect

# Update Status Bar to Yellow (Not Connected)
UPDATE_SCRIPT="/home/linda/PepperProjects/scripts/update_status_bar.py"
if [ -f "$UPDATE_SCRIPT" ] && command -v python3 &> /dev/null; then
    "$UPDATE_SCRIPT" "\$(radio-tower) Not Connected" "#FFC107"
    # Double-tap: Touch the workspace file to force VS Code refresh
    (sleep 1.5 && touch "/home/linda/PepperProjects/PepperAndroid.code-workspace") &
else
    echo "Warning: Status bar update failed (Script or Python missing)"
fi

echo "Cleanup complete. You can now try launching the emulator again."
