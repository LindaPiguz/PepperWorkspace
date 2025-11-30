#!/bin/bash

# Notify user
zenity --info --text="Starting Gradle Continuous Build...\nCheck the 'Auto-Build' terminal for progress." --timeout=3 &

# Run Gradle
./gradlew assembleDebug --continuous
