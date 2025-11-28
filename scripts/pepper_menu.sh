#!/bin/bash
while true; do
    echo "=========================================="
    echo "      Pepper Development Menu"
    echo "=========================================="
    echo "1) Start Pepper Emulator (Auto-Connect)"
    echo "2) Connect Physical Pepper (GUI)"
    echo "3) Robot Viewer"
    echo "4) Animation Editor"
    echo "5) Setup Project"
    echo "6) Gradle Auto-Build"
    echo "q) Quit"
    echo "=========================================="
    read -p "Select an option: " choice

    case $choice in
        1)
            echo "Starting Emulator..."
            nohup ./scripts/launch_emulator_auto_connect.sh >/dev/null 2>&1 &
            ;;
        2)
            nohup ./scripts/connect_physical_robot.sh >/dev/null 2>&1 &
            ;;
        3)
            echo "Connect Robot Viewer to:"
            echo "  a) Emulator (127.0.0.1)"
            echo "  b) Physical Robot"
            read -p "Choice: " viewer_choice
            if [ "$viewer_choice" = "a" ]; then
                echo "Starting Robot Viewer (Emulator)..."
                nohup /home/linda/pepperUtilities/RobotSDK/API\ 7/tools/bin/robot_viewer --ip 127.0.0.1 >/dev/null 2>&1 &
            else
                read -p "Enter Robot IP: " vip
                echo "Starting Robot Viewer ($vip)..."
                nohup /home/linda/pepperUtilities/RobotSDK/API\ 7/tools/bin/robot_viewer --ip $vip >/dev/null 2>&1 &
            fi
            ;;
        4)
            echo "Starting Animation Editor..."
            nohup /home/linda/pepperUtilities/RobotSDK/Animation_Editor/animation_editor/animation-editor-2.9.5.124-linux64/bin/animation_editor_standalone >/dev/null 2>&1 &
            ;;
        5)
            ./scripts/setup_project.sh
            ;;
        6)
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
