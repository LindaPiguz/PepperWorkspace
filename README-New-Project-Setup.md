# New Project Setup Guide

This guide explains how to add a new Android project (or configure an existing one) to the Pepper Workspace.

## 1. Add Project to Workspace
1.  Open VS Code.
2.  Go to **File > Add Folder to Workspace...**
3.  Select your Android project folder (e.g., `MyNewApp`).

## 2. Run the Setup Script
We have a script that automatically configures your project for the "Smart Build" workflow.

1.  Open the **Pepper Menu** (`Ctrl+Shift+B` -> `0. Open Pepper Menu`).
2.  Select option **3. Setup Project**.
3.  Enter the **absolute path** to your project folder (e.g., `/home/linda/AndroidStudioProjects/MyNewApp`).
    *   *Tip: You can drag and drop the folder into the terminal to paste the path.*

### What the Script Does:
*   **`local.properties`**: Updates the `sdk.dir` to point to the modern Android SDK (`/home/linda/Android/Sdk`), preserving your existing settings.
*   **`.vscode/tasks.json`**: Creates a "Smart Build" task that uses our generic build script.
*   **`.vscode/launch.json`**: Creates a debug configuration that attaches to the app after the Smart Build task completes.

## 3. Verify Configuration
1.  Open a file in your new project.
2.  Press **F5**.
3.  You should see the **Smart Build** dialog asking for:
    *   Flavor (if defined in `build.gradle`)
    *   Build Type (Debug/Release)
    *   Target Device (if multiple connected)

## 4. Troubleshooting
*   **"Waiting for Debugger"**: If the app hangs on launch, ensure you selected "Debug" build type. Release builds do not support debugger attachment.
*   **Build Errors**: Check the terminal output. The script prints the full Gradle log.
*   **Missing Flavors**: If the flavor picker is empty, ensure your `build.gradle` defines `productFlavors` correctly.
