#!/bin/bash

# kill_all.sh
# Force kills all emulator and ADB processes to reset the environment.

echo "Killing Emulator processes..."
pkill -9 -f "emulator"
pkill -9 -f "qemu-system"

echo "Killing ADB server..."
adb kill-server

echo "Cleanup complete. You can now try launching the emulator again."
