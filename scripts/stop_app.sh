#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.active_config"

# 1. Resolve Project
source "$SCRIPT_DIR/resolve_project.sh"

if [ -z "$PEPPER_PACKAGE" ]; then
    echo -e "${RED}Error: Could not resolve active project package.${NC}"
    exit 1
fi

echo -e "Stopping app: ${GREEN}$PEPPER_PACKAGE${NC}..."

# 2. Force Stop App
adb shell am force-stop "$PEPPER_PACKAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}App stopped successfully.${NC}"
else
    echo -e "${RED}Failed to stop app.${NC}"
    exit 1
fi
