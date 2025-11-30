#!/bin/bash
while true; do
    echo "=========================================="
    echo "      Pepper Development Menu"
    echo "=========================================="
    echo "1) Start Pepper Emulator (Auto-Connect)"
    echo "2) Connect Physical Pepper (GUI)"
    echo "3) Setup Project"
    echo "4) Gradle Auto-Build"
    echo "q) Quit"
    echo "=========================================="
    read -p "Select an option: " choice

    case $choice in
        1)
            echo "Starting Emulator..."
            ./scripts/launch_emulator_auto_connect.sh
            ;;
        2)
            nohup ./scripts/connect_physical_robot.sh >/dev/null 2>&1 &
            ;;
    
        3)
            ./scripts/setup_project.sh
            ;;
        4)
            ./gradlew assembleDebug --continuous
            ;;
        q)
            echo "Exiting."
            exit 0
            ;;
        *)
            echo "Invalid option."
            ;;
    esac
    echo "Launched. Press Enter to continue..."
    read
done
