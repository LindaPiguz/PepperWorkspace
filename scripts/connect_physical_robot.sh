#!/bin/bash

ADB="/home/linda/Android/Sdk/platform-tools/adb"

HISTORY_FILE="$HOME/.pepper_ip_history"
touch "$HISTORY_FILE"

# Launch Python GUI
SCRIPT_DIR=$(dirname "$(realpath "$0")")
GUI_SCRIPT="$SCRIPT_DIR/ip_selection_gui.py"

if [ ! -f "$GUI_SCRIPT" ]; then
    zenity --error --text="Error: ip_selection_gui.py not found!"
    exit 1
fi

# Capture output (IP|is_new)
GUI_OUTPUT=$(python3 "$GUI_SCRIPT")
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Canceled."
    exit 1
fi

# Parse Output
IP=$(echo "$GUI_OUTPUT" | cut -d'|' -f1)
IS_NEW_STR=$(echo "$GUI_OUTPUT" | cut -d'|' -f2)

if [ "$IS_NEW_STR" == "true" ]; then
    IS_NEW_CONNECTION=true
else
    IS_NEW_CONNECTION=false
fi

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
    
    # Update Status Bar
    UPDATE_SCRIPT="/home/linda/PepperProjects/scripts/update_status_bar.py"
    if [ -f "$UPDATE_SCRIPT" ] && command -v python3 &> /dev/null; then
        "$UPDATE_SCRIPT" "\$(plug) Connected to $IP" "#4CAF50"
        # Double-tap: Touch the workspace file after a brief delay to force VS Code refresh
        (sleep 1.5 && touch "/home/linda/PepperProjects/PepperAndroid.code-workspace") &
    else
        # Silently fail or log warning if script/python missing
        echo "Warning: Status bar update failed (Script or Python missing)"
    fi
    
    # Update History Logic
    if [ "$IS_NEW_CONNECTION" = true ]; then
        # Ask user if they want to save this new IP
        if zenity --question --text="Connection Successful!\n\nDo you want to save $IP to your history?"; then
            # Remove IP if exists (deduplicate), then prepend
            grep -v "$IP" "$HISTORY_FILE" > "$HISTORY_FILE.tmp"
            echo "$IP" > "$HISTORY_FILE"
            cat "$HISTORY_FILE.tmp" >> "$HISTORY_FILE"
            rm "$HISTORY_FILE.tmp"
        fi
    else
        # Existing connection: Auto-bump to top
        grep -v "$IP" "$HISTORY_FILE" > "$HISTORY_FILE.tmp"
        echo "$IP" > "$HISTORY_FILE"
        cat "$HISTORY_FILE.tmp" >> "$HISTORY_FILE"
        rm "$HISTORY_FILE.tmp"
    fi
else
    zenity --error --text="Failed to connect:\n$OUTPUT"
fi
