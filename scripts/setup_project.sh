#!/bin/bash

# setup_project.sh
# Configures the current Android project for the PepperAndroid workspace.
# 1. Sets local.properties to the modern SDK.
# 2. Creates a default .vscode/launch.json if missing.

PROJECT_ROOT=$(pwd)
echo "Configuring project in: $PROJECT_ROOT"

# 1. Configure local.properties
LOCAL_PROPS="$PROJECT_ROOT/local.properties"
MODERN_SDK="/home/linda/Android/Sdk"

if [ -f "$LOCAL_PROPS" ] && grep -q "sdk.dir" "$LOCAL_PROPS"; then
    echo "local.properties already exists and has sdk.dir. Skipping SDK configuration to preserve Android Studio settings."
else
    echo "Setting sdk.dir to $MODERN_SDK in local.properties..."
    echo "sdk.dir=$MODERN_SDK" > "$LOCAL_PROPS"
fi

# 2. Configure launch.json
VSCODE_DIR="$PROJECT_ROOT/.vscode"
LAUNCH_JSON="$VSCODE_DIR/launch.json"

if [ ! -d "$VSCODE_DIR" ]; then
    mkdir -p "$VSCODE_DIR"
fi

if [ ! -f "$LAUNCH_JSON" ]; then
    echo "Creating default launch.json..."
    
    # Attempt to extract package name from AndroidManifest.xml
    MANIFEST="$PROJECT_ROOT/app/src/main/AndroidManifest.xml"
    PACKAGE_NAME=""
    
    if [ -f "$MANIFEST" ]; then
        # Try to find 'package="com.example"' or similar. 
        # Note: Modern Gradle projects might not have package in manifest, but namespace in build.gradle.
        # This is a best-effort grep.
        PACKAGE_NAME=$(grep -oP 'package="\K[^"]+' "$MANIFEST")
    fi
    
    if [ -z "$PACKAGE_NAME" ]; then
        # Fallback: try to find namespace in build.gradle
        BUILD_GRADLE="$PROJECT_ROOT/app/build.gradle"
        if [ -f "$BUILD_GRADLE" ]; then
             PACKAGE_NAME=$(grep -oP "namespace\s+'\K[^']+" "$BUILD_GRADLE")
        fi
    fi

    if [ -z "$PACKAGE_NAME" ]; then
        echo "WARNING: Could not detect package name. Using placeholder."
        PACKAGE_NAME="com.example.myapp.MainActivity"
    else
        echo "Detected package: $PACKAGE_NAME"
        PACKAGE_NAME="${PACKAGE_NAME}.MainActivity"
    fi

    # Create tasks.json for Smart Build
    TASKS_JSON="$VSCODE_DIR/tasks.json"
    cat <<EOF > "$TASKS_JSON"
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Smart Build (Pick Flavor)",
            "type": "shell",
            "command": "\${workspaceFolder}/../scripts/build_generic_app.py \${workspaceFolder}",
            "presentation": {
                "reveal": "always",
                "panel": "dedicated"
            },
            "isBackground": true,
            "problemMatcher": {
                "pattern": [
                    {
                        "regexp": ".",
                        "file": 1,
                        "location": 2,
                        "message": 3
                    }
                ],
                "background": {
                    "activeOnStart": true,
                    "beginsPattern": "^Starting Gradle Build",
                    "endsPattern": "^App Launched!"
                }
            }
        }
    ]
}
EOF

    # Create launch.json
    cat <<EOF > "$LAUNCH_JSON"
{
    "version": "0.2.0",
    "configurations": [
        {
            "type": "android",
            "request": "launch",
            "name": "Run on Device (Smart Build)",
            "mainActivity": "$PACKAGE_NAME",
            "apkFile": "\${workspaceFolder}/app/build/outputs/apk/debug/selected-debug.apk",
            "preLaunchTask": "Smart Build (Pick Flavor)",
            "deviceId": ""
        }
    ]
}
EOF
else
    echo "launch.json already exists. Skipping creation."
fi

echo "Setup complete!"
