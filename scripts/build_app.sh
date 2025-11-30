#!/bin/bash

# build_app.sh
# Builds the active project using Gradle.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Resolve Project
source "$SCRIPT_DIR/resolve_project.sh"

echo "Building Project: $PROJECT_DIR"

cd "$PROJECT_DIR" || exit 1

# 2. Run Smart Build (Build Only)
"$SCRIPT_DIR/smart_build.py" --action build "$PROJECT_DIR"

if [ $? -eq 0 ]; then
    if command -v zenity &> /dev/null; then
        zenity --info --text="Build Successful!" --timeout=3
    fi
else
    # smart_build.py already prints errors
    exit 1
fi
