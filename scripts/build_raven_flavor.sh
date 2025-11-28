#!/bin/bash

PROJECT_DIR="/home/linda/AndroidStudioProjects/Raven"
LAUNCH_JSON="$PROJECT_DIR/.vscode/launch.json"
BASE_PACKAGE="it.diunito.raven"

# 1. Select Flavor & Build Type
# We list all valid combinations
# 1. Select Flavor & Build Type
# We list all valid combinations
CHOICE=$(zenity --list --title="Select Build Variant" --text="Choose the variant to build:" \
    --radiolist --column="Pick" --column="Key" --column="Description" \
    TRUE "ProdPepperDebug" "Prod Pepper (Debug)" \
    FALSE "ProdPepperRelease" "Prod Pepper (Release)" \
    FALSE "ProdDeviceDebug" "Prod Device (Debug)" \
    FALSE "ProdDeviceRelease" "Prod Device (Release)" \
    FALSE "FastTestPepperDebug" "Fast Test Pepper (Debug)" \
    FALSE "FastTestDeviceDebug" "Fast Test Device (Debug)")

if [ -z "$CHOICE" ]; then
    echo "Cancelled."
    exit 1
fi

case $CHOICE in
    "ProdPepperDebug")
        TASK="assembleProdPepperDebug"
        PACKAGE="${BASE_PACKAGE}.pepper.debug"
        APK_PATH="app/build/outputs/apk/prodPepper/debug/app-prod-pepper-debug.apk"
        IS_DEBUG="true"
        ;;
    "ProdPepperRelease")
        TASK="assembleProdPepperRelease"
        PACKAGE="${BASE_PACKAGE}.pepper"
        # Release APKs might be unsigned or named differently. We'll search for it later or assume standard.
        APK_PATH="app/build/outputs/apk/prodPepper/release/app-prod-pepper-release.apk"
        IS_DEBUG="false"
        ;;
    "ProdDeviceDebug")
        TASK="assembleProdDeviceDebug"
        PACKAGE="${BASE_PACKAGE}.debug"
        APK_PATH="app/build/outputs/apk/prodDevice/debug/app-prod-device-debug.apk"
        IS_DEBUG="true"
        ;;
    "ProdDeviceRelease")
        TASK="assembleProdDeviceRelease"
        PACKAGE="${BASE_PACKAGE}"
        APK_PATH="app/build/outputs/apk/prodDevice/release/app-prod-device-release.apk"
        IS_DEBUG="false"
        ;;
    "FastTestPepperDebug")
        TASK="assembleFastTestModePepperDebug"
        PACKAGE="${BASE_PACKAGE}.fast.pepper.debug"
        APK_PATH="app/build/outputs/apk/fastTestModePepper/debug/app-fastTestMode-pepper-debug.apk"
        IS_DEBUG="true"
        ;;
    "FastTestDeviceDebug")
        TASK="assembleFastTestModeDeviceDebug"
        PACKAGE="${BASE_PACKAGE}.fast.debug"
        APK_PATH="app/build/outputs/apk/fastTestModeDevice/debug/app-fastTestMode-device-debug.apk"
        IS_DEBUG="true"
        ;;
esac

echo "Selected: $CHOICE"
echo "Package: $PACKAGE"
echo "Task: $TASK"

# 3. Update launch.json with new package name
# We need to set it to "attach" mode now that we handle the launch
sed -i "s/\"request\": \"launch\"/\"request\": \"attach\"/" "$LAUNCH_JSON"
sed -i "s/\"mainActivity\": \".*\"/\"mainActivity\": \"$PACKAGE.MainActivity\"/" "$LAUNCH_JSON"

# 4. Build (Direct Output)
cd "$PROJECT_DIR"
echo "=========================================="
echo "Starting Gradle Build: $TASK"
echo "=========================================="
./gradlew "$TASK"

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "=========================================="
    echo "BUILD FAILED!"
    echo "=========================================="
    exit $EXIT_CODE
fi

# Check if the APK exists
if [ ! -f "$APK_PATH" ]; then
    # Fallback: Search for any APK in the expected folder (e.g. release unsigned)
    SEARCH_DIR=$(dirname "$APK_PATH")
    FOUND_APK=$(find "$SEARCH_DIR" -name "*.apk" | head -n 1)
    if [ -n "$FOUND_APK" ]; then
        echo "Warning: Exact APK path not found. Using found APK: $FOUND_APK"
        APK_PATH="$FOUND_APK"
    else
        echo "Error: APK not found at $APK_PATH"
        exit 1
    fi
fi

# 5. Select Device (if multiple)
DEVICES=$(adb devices | grep -v "List" | grep "device$" | awk '{print $1}')
COUNT=$(echo "$DEVICES" | wc -l)

if [ "$COUNT" -eq 0 ]; then
    echo "Error: No devices connected!"
    exit 1
elif [ "$COUNT" -eq 1 ]; then
    DEVICE_SERIAL=$(echo "$DEVICES" | tr -d '[:space:]')
else
    # Multiple devices: Ask user
    # Prepare list for Zenity
    ZENITY_ARGS=()
    for dev in $DEVICES; do
        ZENITY_ARGS+=(FALSE "$dev")
    done
    # Set first one as TRUE (default)
    ZENITY_ARGS[0]="TRUE"
    
    DEVICE_SERIAL=$(zenity --list --title="Select Device" --text="Multiple devices found. Choose target:" \
        --radiolist --column="Pick" --column="Serial" "${ZENITY_ARGS[@]}")
    
    if [ -z "$DEVICE_SERIAL" ]; then
        echo "Device selection cancelled."
        exit 1
    fi
fi

echo "Target Device: $DEVICE_SERIAL"

# 6. Install and Launch
echo "=========================================="
echo "Installing APK to $DEVICE_SERIAL..."
echo "=========================================="
adb -s "$DEVICE_SERIAL" install -r "$APK_PATH"

echo "=========================================="
echo "Launching App on $DEVICE_SERIAL..."
echo "=========================================="

if [ "$IS_DEBUG" = "true" ]; then
    # Launch without -D (don't wait for debugger) to avoid hanging if attach fails
    adb -s "$DEVICE_SERIAL" shell am start -n "$PACKAGE/$BASE_PACKAGE.MainActivity"
    echo "=========================================="
    echo "App Launched! (Debug Mode - Attempting to Attach...)"
    echo "=========================================="
else
    # Launch immediately (Release mode)
    adb -s "$DEVICE_SERIAL" shell am start -n "$PACKAGE/$BASE_PACKAGE.MainActivity"
    echo "=========================================="
    echo "App Launched! (Release Mode - Debugger will NOT attach)"
    echo "=========================================="
fi


# 5. Copy APK to fixed location
DEST_APK="app/build/outputs/apk/debug/selected-debug.apk"
mkdir -p "app/build/outputs/apk/debug"
cp "$APK_PATH" "$DEST_APK"

echo "Build successful. APK ready at $DEST_APK"
