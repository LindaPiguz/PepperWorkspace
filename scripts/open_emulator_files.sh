#!/bin/bash

# Try to open the Downloads folder directly
adb shell am start -a android.intent.action.VIEW -d "file:///sdcard/Download" -t "*/*"

# If that fails (no app handles it), try a generic file picker
if [ $? -ne 0 ]; then
    echo "Direct view failed, trying generic picker..."
    adb shell am start -a android.intent.action.GET_CONTENT -t "*/*"
fi
