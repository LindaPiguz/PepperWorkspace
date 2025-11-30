#!/bin/bash

# resolve_project.sh
# Helper script to determine the active Android project.
# 1. Checks .active_config
# 2. If missing/invalid, scans workspace for projects.
# 3. If multiple found, prompts user.
# 4. Updates .active_config.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.active_config"
WORKSPACE_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to update config
update_config() {
    local proj_dir="$1"
    local pkg_name="$2"
    
    echo "# Active Project Configuration" > "$CONFIG_FILE"
    echo "PROJECT_DIR=\"$proj_dir\"" >> "$CONFIG_FILE"
    echo "PEPPER_PACKAGE=\"$pkg_name\"" >> "$CONFIG_FILE"
}

# Function to detect package name
detect_package() {
    local proj_dir="$1"
    local manifest="$proj_dir/app/src/main/AndroidManifest.xml"
    local build_gradle="$proj_dir/app/build.gradle"
    local pkg=""

    if [ -f "$manifest" ]; then
        pkg=$(grep -oP 'package="\K[^"]+' "$manifest")
    fi
    
    if [ -z "$pkg" ] && [ -f "$build_gradle" ]; then
        pkg=$(grep -oP "namespace\s+'\K[^']+" "$build_gradle")
    fi
    
    echo "$pkg"
}

# 1. Check existing config
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    if [ -d "$PROJECT_DIR" ] && [ ! -z "$PEPPER_PACKAGE" ]; then
        # Config is valid
        export PROJECT_DIR
        export PEPPER_PACKAGE
        return 0
    fi
fi

# 2. Scan for projects (folders with build.gradle)
# Exclude the workspace root itself if it has one (unlikely but safe)
PROJECTS=()
while IFS= read -r -d '' file; do
    dir=$(dirname "$file")
    # Check if it's an app module or root project
    if [ -f "$dir/app/build.gradle" ] || [ -f "$dir/build.gradle" ]; then
        # Avoid duplicates (if we found root and app)
        # We prefer the root of the android project
        if [ -f "$dir/settings.gradle" ]; then
             PROJECTS+=("$dir")
        fi
    fi
done < <(find "$WORKSPACE_ROOT" -maxdepth 2 -name "build.gradle" -print0)

COUNT=${#PROJECTS[@]}

if [ $COUNT -eq 0 ]; then
    if command -v zenity &> /dev/null; then
        zenity --error --text="No Android projects found in workspace!"
    else
        echo "Error: No Android projects found."
    fi
    exit 1
elif [ $COUNT -eq 1 ]; then
    # Auto-select
    SELECTED_DIR="${PROJECTS[0]}"
    PKG=$(detect_package "$SELECTED_DIR")
    update_config "$SELECTED_DIR" "$PKG"
    export PROJECT_DIR="$SELECTED_DIR"
    export PEPPER_PACKAGE="$PKG"
else
    # Multiple projects - Prompt
    if command -v zenity &> /dev/null; then
        # Format list for Zenity
        OPTIONS=()
        for p in "${PROJECTS[@]}"; do
            OPTIONS+=("$(basename "$p")" "$p")
        done
        
        SELECTED_DIR=$(zenity --list --title="Select Active Project" --column="Name" --column="Path" "${OPTIONS[@]}" --hide-column=2 --print-column=2)
        
        if [ -z "$SELECTED_DIR" ]; then
            exit 1 # User cancelled
        fi
        
        PKG=$(detect_package "$SELECTED_DIR")
        update_config "$SELECTED_DIR" "$PKG"
        export PROJECT_DIR="$SELECTED_DIR"
        export PEPPER_PACKAGE="$PKG"
    else
        echo "Multiple projects found. Please run 'Setup Current Project' task to select one."
        exit 1
    fi
fi
