#!/bin/bash

# build_app.sh
# Builds the active project using Gradle.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Resolve Project
source "$SCRIPT_DIR/resolve_project.sh"

echo "Building Project: $PROJECT_DIR"

cd "$PROJECT_DIR" || exit 1

# 2. Run Gradle Build
./gradlew assembleDebug

if [ $? -eq 0 ]; then
    if command -v zenity &> /dev/null; then
        zenity --info --text="Build Successful!" --timeout=3
    fi
else
    if command -v zenity &> /dev/null; then
        zenity --error --text="Build Failed! Check terminal for details."
    fi
    exit 1
fi
