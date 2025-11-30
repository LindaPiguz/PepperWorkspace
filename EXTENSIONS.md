# 🧩 Recommended Extensions for Pepper Android Workspace

This document lists the essential extensions required to effectively use this workspace. They are categorized by purpose to help you understand why each one is needed.

## ⚙️ Marketplace Setup (Troubleshooting)
If you cannot find these extensions in your editor, you may need to configure the Marketplace URLs to point to the official Visual Studio Marketplace.

**Recommended Settings:**
*   **Marketplace Item URL**: `https://marketplace.visualstudio.com/items`
*   **Marketplace Gallery URL**: `https://marketplace.visualstudio.com/_apis/public/gallery`

> **Note**: You may need to restart your editor after changing these settings.

## 📱 Core Android & Kotlin
*Tools for writing Kotlin code and debugging Android applications.*

### **Kotlin**
*   **Author**: fwcd
*   **ID**: `fwcd.kotlin`
*   **Purpose**: Provides syntax highlighting, code completion, and navigation for Kotlin files (essential for Android development).
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=fwcd.kotlin)

### **Android**
*   **Author**: adelphes
*   **ID**: `adelphes.android`
*   **Purpose**: Adds Android-specific debugging capabilities to VS Code, allowing you to deploy and debug apps on devices.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=adelphes.android)

### **AVD Manager**
*   **Author**: toroxx
*   **ID**: `toroxx.avd-manager`
*   **Purpose**: Allows you to create, manage, and launch Android Virtual Devices (Emulators) directly from the command palette.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=toroxx.avd-manager)

## ☕ Java & Build Tools
*Essential for building the Android project using Gradle.*

### **Extension Pack for Java**
*   **Author**: Microsoft
*   **ID**: `vscjava.vscode-java-pack`
*   **Purpose**: A comprehensive bundle that includes:
    *   **Language Support for Java** (Red Hat) - for Intellisense.
    *   **Debugger for Java** (Microsoft) - for debugging Java code.
    *   **Maven for Java** (Microsoft) - for dependency management.
    *   **Project Manager for Java** (Microsoft) - for project handling.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-pack)

### **Gradle for Java**
*   **Author**: Microsoft
*   **ID**: `vscjava.vscode-gradle`
*   **Purpose**: Provides a visual sidebar to run Gradle tasks (build, clean, install) and view dependencies.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-gradle)

## 🛠️ Workspace Utilities
*Tools that make this specific workspace easier to use.*

### **VsCode Action Buttons**
*   **Author**: Seun LanLege
*   **ID**: `seunlanlege.action-buttons`
*   **Purpose**: Adds the custom buttons ("Emulator", "Connect Pepper", "Monitor Logs") to the bottom status bar for one-click actions.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=seunlanlege.action-buttons)

### **Task Explorer**
*   **Author**: Scott Meesseman
*   **ID**: `spmeesseman.vscode-taskexplorer`
*   **Purpose**: Provides a sidebar view to see and run all available tasks (VS Code tasks, Gradle tasks, etc.) in one place.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=spmeesseman.vscode-taskexplorer)

## 🐍 Python Support
*Required for the custom log monitoring script.*

### **Python**
*   **Author**: Microsoft
*   **ID**: `ms-python.python`
*   **Purpose**: Enables VS Code to run and debug the `monitor_logcat.py` script which filters the Android logs.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

## 🎨 UI & Design
*Helpers for working with colors in your app design.*

### **Color Highlight**
*   **Author**: Sergii N
*   **ID**: `naumovs.color-highlight`
*   **Purpose**: Visually highlights color codes (e.g., `#4CAF50`) in your code so you can see the actual color immediately.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=naumovs.color-highlight)

### **Color Picker**
*   **Author**: anseki
*   **ID**: `anseki.vscode-color`
*   **Purpose**: Provides a GUI to generate color codes easily without leaving the editor.
*   [Download from Marketplace](https://marketplace.visualstudio.com/items?itemName=anseki.vscode-color)
