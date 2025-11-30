# Pepper Android Workspace

This workspace is designed to streamline Android development for SoftBank Robotics' Pepper robot, bridging the gap between modern Android tools and legacy Pepper utilities.

## Architecture: "Modern Build / Legacy Run"

The core philosophy of this environment is to use the best tool for each job:
*   **Building (Modern)**: Uses the latest Android SDK, Gradle, and Java versions (Java 17/21) to ensure compatibility with modern libraries (Compose, Kotlin, etc.).
*   **Running (Legacy)**: Uses the specific Pepper SDK tools (Emulator, `qisdk`) which often require older environments (Java 8/11) or specific paths.

We achieve this by managing environment variables dynamically in our scripts, so you don't have to manually switch Java versions.

## Features

### 1. Unified Pepper Menu
Access all tools via a single menu (`Ctrl+Shift+B` -> `0. Open Pepper Menu`):
*   **Start Emulator**: Launches the Pepper Emulator and automatically connects ADB.
*   **Connect Physical Robot**: GUI to enter IP and connect to a real robot.
*   **Setup Project**: Configures new projects for this workspace.

### 2. Smart Build System
We replaced the standard "Run" button with a smart script (`scripts/build_generic_app.py`) that:
*   **Parses Flavors**: Automatically detects product flavors in your `build.gradle`.
*   **GUI Selection**: Asks you to choose Flavor, Build Type (Debug/Release), and Target Device via a popup.
*   **Auto-Launch**: Installs and launches the app automatically.
*   **Ctrl+C Stop**: Allows you to stop the running app directly from the VS Code terminal.

### 3. Multi-Root Workspace
The workspace (`PepperAndroid.code-workspace`) manages multiple folders:
*   `PepperProjects`: This folder, containing scripts and configuration.
*   `Raven` (and others): Your actual Android application source code.

## Scripts Reference

*   `scripts/pepper_menu.sh`: Main launcher menu.
*   `scripts/build_generic_app.py`: The brain of the build system. Handles Gradle parsing, Zenity UI, ADB commands, and launch logic.
*   `scripts/setup_project.sh`: Helper to configure `local.properties` and `.vscode` files for new projects.
*   `scripts/launch_emulator_auto_connect.sh`: Wrapper to start emulator and ensure ADB connection.
*   `scripts/connect_physical_robot.sh`: Helper for connecting to real hardware.

## Getting Started
1.  **Open Workspace**: File > Open Workspace from File... > `PepperAndroid.code-workspace`.
2.  **Start Emulator**: Use the Pepper Menu.
3.  **Run App**: Open your app folder, press **F5**, and follow the prompts.

## Adding New Projects
See [README-New-Project-Setup.md](README-New-Project-Setup.md) for detailed instructions.

## Recommended Extensions
See [EXTENSIONS.md](EXTENSIONS.md) for a curated list of extensions required for this workspace, including setup instructions.
