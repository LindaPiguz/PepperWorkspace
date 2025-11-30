#!/bin/bash

# Start the emulator wrapper in the background
echo "Starting Emulator..."
/home/linda/pepperUtilities/emulator/start_emulator_wrapper.sh &
EMULATOR_PID=$!

# Wait for the emulator to be ready (simple loop trying to connect)
echo "Waiting for emulator to become ready..."
ADB="/home/linda/Android/Sdk/platform-tools/adb"

# Loop for up to 60 seconds
for i in {1..30}; do
    echo "Attempt $i/30: Connecting to localhost:5555..."
    sleep 2
    if $ADB connect localhost:5555 | grep -q "connected"; then
        echo "Emulator Connected!"
        zenity --info --text="Pepper Emulator Connected Successfully!" --timeout=5
        exit 0
    fi
done

echo "Timed out waiting for emulator connection."
zenity --error --text="Failed to auto-connect to Emulator."
exit 1
