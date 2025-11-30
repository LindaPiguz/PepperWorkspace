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
    echo "Attempt $i/30: Connecting to emulator..."
    
    # Check if emulator-5554 is already connected (standard)
    if $ADB devices | grep -q "emulator-5554.*device"; then
        echo "Standard emulator-5554 detected."
    else
        # Try explicit connect if not found
        $ADB connect localhost:5555
    fi
    sleep 2
    # Determine which serial to use
    if $ADB devices | grep -q "emulator-5554.*device"; then
        TARGET_SERIAL="emulator-5554"
    else
        TARGET_SERIAL="localhost:5555"
    fi

    if $ADB -s $TARGET_SERIAL shell getprop sys.boot_completed | grep -q "1"; then
        echo "Emulator Connected ($TARGET_SERIAL)!"
        
        # Load Active Configuration if available
        SCRIPT_DIR=$(dirname "$(realpath "$0")")
        CONFIG_FILE="$SCRIPT_DIR/.active_config"
        
        if [ -f "$CONFIG_FILE" ]; then
            source "$CONFIG_FILE"
        fi

        # Arguments override config
        PROJECT_DIR="${1:-$PROJECT_DIR}"
        PEPPER_PACKAGE="${2:-$PEPPER_PACKAGE}"
        
        # Default fallback if still empty
        PEPPER_PACKAGE="${PEPPER_PACKAGE:-NO_ACTIVE_PACKAGE_FILTER}"

        if [ -n "$PROJECT_DIR" ]; then
            cd "$PROJECT_DIR"
            echo "Switched to Project: $(pwd)"
        fi

        # Clear terminal screen
        clear
        
        echo "===================================================="
        echo "      Emulator Connected: $TARGET_SERIAL"
        echo "      Ready for use with Android Extension."
        echo "===================================================="
        
        # Pause to let the user see the status
        echo "Press Enter to close this window..."
        read
        exit 0
    fi
done

echo "Timed out waiting for emulator connection."
echo "Press Enter to exit..."
read
exit 1
