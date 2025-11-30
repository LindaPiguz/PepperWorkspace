#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.active_config"

# 1. Resolve Project
source "$SCRIPT_DIR/resolve_project.sh"

if [ -z "$PROJECT_DIR" ] || [ -z "$PEPPER_PACKAGE" ]; then
    echo -e "${RED}Error: Could not resolve active project.${NC}"
    exit 1
fi

echo -e "${YELLOW}Target Project:${NC} $PROJECT_DIR"

# 2. Run Smart Build (Build & Run)
"$SCRIPT_DIR/smart_build.py" --action run "$PROJECT_DIR"

if [ $? -ne 0 ]; then
    echo -e "${RED}Operation Failed!${NC}"
    exit 1
fi

echo -e "\n${GREEN}Done!${NC}"
