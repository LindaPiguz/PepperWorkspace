#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import glob

# Configuration
SDK_DIR = "/home/linda/Android/Sdk"
BUILD_TOOLS_DIR = glob.glob(os.path.join(SDK_DIR, "build-tools", "*"))[-1] # Use latest
AAPT = os.path.join(BUILD_TOOLS_DIR, "aapt")

def run_zenity(args):
    try:
        result = subprocess.run(["zenity"] + args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def parse_gradle(gradle_path):
    with open(gradle_path, 'r') as f:
        content = f.read()
    
    # Extract dimensions
    dims_match = re.search(r'flavorDimensions\s+(.*)', content)
    dimensions = []
    if dims_match:
        # Clean up string: "mode", "device" -> ['mode', 'device']
        raw = dims_match.group(1)
        # Remove comments
        raw = re.sub(r'//.*', '', raw)
        dimensions = [d.strip().strip('"\'') for d in raw.split(',')]

    # Extract flavors
    flavors = {} # {dimension: [flavor_names]}
    
    # Find productFlavors block start
    start_match = re.search(r'productFlavors\s*\{', content)
    if start_match:
        start_idx = start_match.end()
        # Brace counting to find the end of the block
        brace_count = 1
        i = start_idx
        while i < len(content) and brace_count > 0:
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
            i += 1
        
        block_content = content[start_idx:i-1]
        
        # Find flavor definitions: name { ... }
        # We look for words followed by {
        # This regex matches "name {"
        flavor_defs = re.finditer(r'(\w+)\s*\{', block_content)
        
        for match in flavor_defs:
            name = match.group(1)
            # Find the body of this flavor to extract dimension
            f_start = match.end()
            f_brace = 1
            j = f_start
            while j < len(block_content) and f_brace > 0:
                if block_content[j] == '{':
                    f_brace += 1
                elif block_content[j] == '}':
                    f_brace -= 1
                j += 1
            
            f_body = block_content[f_start:j-1]
            
            dim_match = re.search(r'dimension\s+["\'](\w+)["\']', f_body)
            if dim_match:
                dim = dim_match.group(1)
                if dim not in flavors:
                    flavors[dim] = []
                flavors[dim].append(name)
    
    return dimensions, flavors

def select_device():
    try:
        out = subprocess.check_output(["adb", "devices"], text=True)
        lines = out.strip().split('\n')[1:] # Skip header
        devices = [line.split()[0] for line in lines if "device" in line and not "List" in line]
        
        if not devices:
            print("Error: No devices connected!")
            sys.exit(1)
        
        # Deduplicate: If emulator-5554 is present, ignore localhost:5555 (they are likely the same)
        if "emulator-5554" in devices and "localhost:5555" in devices:
            devices.remove("localhost:5555")
            
        if len(devices) == 1:
            return devices[0]
        
        # Multiple devices
        zenity_args = ["--list", "--title=Select Device", "--text=Multiple devices found. Choose target:", "--column=Serial"] + devices
        choice = run_zenity(zenity_args)
        if not choice:
            print("Device selection cancelled.")
            sys.exit(1)
        return choice
    except Exception as e:
        print(f"Error selecting device: {e}")
        sys.exit(1)

def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description='Build Android App')
    parser.add_argument('project_root', help='Root directory of the project')
    parser.add_argument('--flavor', action='append', help='Specify flavor (e.g. mode=prod)')
    parser.add_argument('--build-type', help='Specify build type (Debug or Release)')
    args = parser.parse_args()

    project_root = args.project_root
    app_dir = os.path.join(project_root, "app")
    gradle_file = os.path.join(app_dir, "build.gradle")
    launch_json = os.path.join(project_root, ".vscode", "launch.json")

    if not os.path.exists(gradle_file):
        print("No build.gradle found.")
        sys.exit(1)

    dimensions, flavors = parse_gradle(gradle_file)
    
    selected_flavors = []
    
    if not dimensions:
        print("No flavors found. Building default debug.")
        task = "assembleDebug"
        build_type = "Debug" # Default
    else:
        # Check if flavors are provided via CLI
        cli_flavors = {}
        if args.flavor:
            for f in args.flavor:
                if '=' in f:
                    k, v = f.split('=', 1)
                    cli_flavors[k] = v
                else:
                    # Try to guess dimension? No, strict format needed or just value matching
                    pass

        # Ask user for each dimension if not provided
        for dim in dimensions:
            if dim in cli_flavors:
                selected_flavors.append(cli_flavors[dim])
            else:
                options = flavors.get(dim, [])
                if not options:
                    continue
                
                # Prepare Zenity list
                zenity_args = ["--list", "--title=Select " + dim.capitalize(), "--text=Choose " + dim, "--column=Flavor"] + options
                choice = run_zenity(zenity_args)
                if not choice:
                    print("Cancelled.")
                    sys.exit(1)
                selected_flavors.append(choice)
        
        # Construct task name: assemble[Flavor1][Flavor2]...[BuildType]
        # Capitalize flavors
        caps_flavors = "".join([f[0].upper() + f[1:] for f in selected_flavors])
    
    # Ask for Build Type if not provided
    if args.build_type:
        build_type = args.build_type
    else:
        build_type = run_zenity(["--list", "--title=Select Build Type", "--text=Choose Build Type", "--column=Type", "Debug", "Release"])
        if not build_type:
            print("Cancelled.")
            sys.exit(1)
        
    task = f"assemble{caps_flavors}{build_type}"
    is_debug = (build_type == "Debug")

    print(f"Building Task: {task}")
    
    # Run Gradle (Direct Output)
    gradlew = os.path.join(project_root, "gradlew")
    print("==========================================")
    print(f"Starting Gradle Build: {task}")
    print("==========================================")
    
    try:
        subprocess.run([gradlew, task], cwd=project_root, check=True)
    except subprocess.CalledProcessError:
        print("==========================================")
        print("BUILD FAILED!")
        print("==========================================")
        sys.exit(1)

    # Find the APK
    # Search for *-debug.apk or *-release.apk based on build type
    suffix = "debug.apk" if is_debug else "release.apk"
    # Also handle unsigned release APKs
    apk_pattern = os.path.join(app_dir, "build", "outputs", "apk", "**", f"*-{suffix}")
    if not is_debug:
        # Try to find any apk if specific release one fails (e.g. unsigned)
        apk_pattern_fallback = os.path.join(app_dir, "build", "outputs", "apk", "**", "*.apk")
    
    apks = glob.glob(apk_pattern, recursive=True)
    if not apks and not is_debug:
        apks = glob.glob(apk_pattern_fallback, recursive=True)
        
    apks = [a for a in apks if "selected-debug.apk" not in a]

    if not apks:
        print("Error: Could not find generated APK.")
        sys.exit(1)
        
    latest_apk = max(apks, key=os.path.getctime)
    
    # Copy to fixed location
    dest_apk = os.path.join(app_dir, "build", "outputs", "apk", "debug", "selected-debug.apk")
    os.makedirs(os.path.dirname(dest_apk), exist_ok=True)
    os.system(f"cp '{latest_apk}' '{dest_apk}'")
    
    # Extract Package Name using AAPT
    try:
        aapt_out = subprocess.check_output([AAPT, "dump", "badging", dest_apk], text=True)
        pkg_match = re.search(r"package: name='([^']+)'", aapt_out)
        if pkg_match:
            pkg_name = pkg_match.group(1)
            print(f"Detected Package: {pkg_name}")
            
            # Select Device
            device_serial = select_device()
            print(f"Target Device: {device_serial}")
            
            # Install and Launch
            print("==========================================")
            print(f"Installing APK to {device_serial}...")
            print("==========================================")
            subprocess.run(["adb", "-s", device_serial, "install", "-r", dest_apk], check=True)
            
            # Detect Launchable Activity
            act_match = re.search(r"launchable-activity: name='([^']+)'", aapt_out)
            launch_act = f"{pkg_name}.MainActivity" # Default
            if act_match:
                launch_act = act_match.group(1)
            
            print("==========================================")
            print(f"Launching {launch_act} on {device_serial}...")
            print("==========================================")
            
            if is_debug:
                # Launch without -D (don't wait for debugger)
                subprocess.run(["adb", "-s", device_serial, "shell", "am", "start", "-n", f"{pkg_name}/{launch_act}"], check=True)
                print("==========================================")
                print("App Launched! (Debug Mode - Attempting to Attach...)")
                print("==========================================")
            else:
                # Launch immediately
                subprocess.run(["adb", "-s", device_serial, "shell", "am", "start", "-n", f"{pkg_name}/{launch_act}"], check=True)
                print("==========================================")
                print("App Launched! (Release Mode - Debugger will NOT attach)")
                print("==========================================")

            # Update launch.json
            if os.path.exists(launch_json):
                with open(launch_json, 'r') as f:
                    js_content = f.read()
                
                # Update request type to attach
                js_content = re.sub(r'"request":\s*"launch"', '"request": "attach"', js_content)
                # Update mainActivity
                js_content = re.sub(r'"mainActivity":\s*".*"', f'"mainActivity": "{launch_act}"', js_content)
                
                with open(launch_json, 'w') as f:
                    f.write(js_content)
                print("Updated launch.json to 'attach' mode")

            # Wait for Ctrl+C to stop app
            print("\n" + "="*42)
            print(f"App is running on {device_serial}.")
            print("Press Ctrl+C to STOP the app and exit.")
            print("="*42)
            try:
                subprocess.run(["cat"], check=False) # Dummy wait
            except KeyboardInterrupt:
                print("\nStopping App...")
                subprocess.run(["adb", "-s", device_serial, "shell", "am", "force-stop", pkg_name], check=False)
                print("App Stopped.")
                sys.exit(0)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"Error during deployment: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
