#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR=$(dirname "$(realpath "$0")")
WORKSPACE_DIR=$(dirname "$SCRIPT_DIR")
WORKSPACE_FILE="$WORKSPACE_DIR/PepperAndroid.code-workspace"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Pepper Android Workspace Setup       ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. List Recommended Extensions
echo -e "${YELLOW}Required Extensions:${NC}"
if [ -f "$WORKSPACE_FILE" ]; then
    # Extract extensions from the JSON file using grep/sed (simple parsing)
    grep -A 20 '"recommendations": \[' "$WORKSPACE_FILE" | grep -v "recommendations" | grep -v "\[" | sed '/]/q' | sed 's/^[ \t]*//;s/[",]//g' | while read -r ext; do
        if [ ! -z "$ext" ] && [ "$ext" != "]" ]; then
             echo -e "  - ${GREEN}$ext${NC}"
        fi
    done
else
    echo "  (Could not read workspace file to list extensions)"
fi

echo ""
echo -e "${YELLOW}Opening Documentation...${NC}"

# 2. Detect Editor and Open Files
# We prioritize 'antigravity' as requested, then 'code', then others.

FILES_TO_OPEN="$WORKSPACE_DIR/README.md $WORKSPACE_DIR/README-New-Project-Setup.md"

if command -v antigravity &> /dev/null; then
    echo "Detected Editor: Antigravity"
    antigravity -r $FILES_TO_OPEN
elif command -v code &> /dev/null; then
    echo "Detected Editor: VS Code"
    code -r $FILES_TO_OPEN
elif command -v cursor &> /dev/null; then
    echo "Detected Editor: Cursor"
    cursor -r $FILES_TO_OPEN
else
    echo -e "${YELLOW}Could not detect a known editor CLI (antigravity, code, cursor).${NC}"
    echo "Please manually open the following files:"
    echo "  - README.md"
    echo "  - README-New-Project-Setup.md"
fi

echo ""
echo -e "${BLUE}Setup Complete!${NC}"
