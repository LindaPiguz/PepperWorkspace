#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.active_config"

# 1. Load Configuration
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo -e "${RED}Error: Configuration file not found at $CONFIG_FILE${NC}"
    echo "Please run the Setup Project script first."
    exit 1
fi

if [ -z "$PROJECT_DIR" ] || [ -z "$PEPPER_PACKAGE" ]; then
    echo -e "${RED}Error: PROJECT_DIR or PEPPER_PACKAGE not defined in config.${NC}"
    exit 1
fi

echo -e "${YELLOW}Target Project:${NC} $PROJECT_DIR"
echo -e "${YELLOW}Package:${NC} $PEPPER_PACKAGE"

cd "$PROJECT_DIR" || exit 1

# 2. Build (AssembleDebug)
echo -e "\n${YELLOW}Building APK...${NC}"
./gradlew assembleDebug

if [ $? -ne 0 ]; then
    echo -e "${RED}Build Failed!${NC}"
    exit 1
fi

# 3. Install
echo -e "\n${YELLOW}Installing APK...${NC}"
# Find the APK (handling potential variations in output path)
APK_PATH=$(find app/build/outputs/apk/debug -name "*.apk" | head -n 1)

if [ -z "$APK_PATH" ]; then
    echo -e "${RED}Error: Could not find generated APK in app/build/outputs/apk/debug${NC}"
    exit 1
fi

adb install -r "$APK_PATH"

if [ $? -ne 0 ]; then
    echo -e "${RED}Install Failed!${NC}"
    exit 1
fi

# 4. Launch
echo -e "\n${YELLOW}Launching App...${NC}"
adb shell monkey -p "$PEPPER_PACKAGE" -c android.intent.category.LAUNCHER 1

echo -e "\n${GREEN}Done! App is running.${NC}"
