#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import glob
import tkinter as tk
from tkinter import ttk, messagebox

# Configuration
SDK_DIR = "/home/linda/Android/Sdk"
# specific build tools version might be needed, but let's try to find the latest
try:
    BUILD_TOOLS_DIR = glob.glob(os.path.join(SDK_DIR, "build-tools", "*"))[-1]
    AAPT = os.path.join(BUILD_TOOLS_DIR, "aapt")
except IndexError:
    AAPT = "aapt" # Hope it's in path

class BuildDialog:
    def __init__(self, root, dimensions, flavors, devices, on_submit):
        self.root = root
        self.root.title("Build Configuration")
        self.on_submit = on_submit
        self.result = None
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        
        # --- Build Type ---
        ttk.Label(main_frame, text="Build Type", font=('Helvetica', 12, 'bold')).grid(row=row, column=0, sticky="w", pady=(0, 5))
        row += 1
        
        self.build_type_var = tk.StringVar(value="Debug")
        bt_frame = ttk.Frame(main_frame)
        bt_frame.grid(row=row, column=0, sticky="w", pady=(0, 15))
        ttk.Radiobutton(bt_frame, text="Debug", variable=self.build_type_var, value="Debug").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(bt_frame, text="Release", variable=self.build_type_var, value="Release").pack(side=tk.LEFT)
        row += 1

        # --- Device ---
        ttk.Label(main_frame, text="Device", font=('Helvetica', 12, 'bold')).grid(row=row, column=0, sticky="w", pady=(0, 5))
        row += 1
        
        self.device_var = tk.StringVar()
        dev_frame = ttk.Frame(main_frame)
        dev_frame.grid(row=row, column=0, sticky="w", pady=(0, 15))
        
        if not devices:
            ttk.Label(dev_frame, text="No devices connected", foreground="red").pack(side=tk.LEFT)
            self.device_var.set(None)
        else:
            self.device_var.set(devices[0]) # Default to first
            for dev in devices:
                # Clean up serial for display if possible, but serial is needed for adb
                ttk.Radiobutton(dev_frame, text=dev, variable=self.device_var, value=dev).pack(side=tk.LEFT, padx=(0, 10))
        row += 1

        # --- Flavors ---
        self.flavor_vars = {}
        for dim in dimensions:
            ttk.Label(main_frame, text=dim.capitalize(), font=('Helvetica', 12, 'bold')).grid(row=row, column=0, sticky="w", pady=(0, 5))
            row += 1
            
            f_frame = ttk.Frame(main_frame)
            f_frame.grid(row=row, column=0, sticky="w", pady=(0, 15))
            
            opts = flavors.get(dim, [])
            if opts:
                var = tk.StringVar(value=opts[0])
                self.flavor_vars[dim] = var
                for opt in opts:
                    ttk.Radiobutton(f_frame, text=opt, variable=var, value=opt).pack(side=tk.LEFT, padx=(0, 10))
            else:
                ttk.Label(f_frame, text="No options found").pack(side=tk.LEFT)
            
            row += 1

        # --- Buttons ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=row, column=0, sticky="e", pady=(10, 0))
        
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="Run", command=self.submit).pack(side=tk.LEFT)
        
        # Center window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def submit(self):
        self.result = {
            "build_type": self.build_type_var.get(),
            "device": self.device_var.get(),
            "flavors": {dim: var.get() for dim, var in self.flavor_vars.items()}
        }
        self.root.destroy()

    def cancel(self):
        self.root.destroy()
        sys.exit(1)

def get_connected_devices():
    try:
        out = subprocess.check_output(["adb", "devices"], text=True)
        lines = out.strip().split('\n')[1:]
        devices = [line.split()[0] for line in lines if "device" in line and "List" not in line]
        # Dedupe emulator/localhost
        if "emulator-5554" in devices and "localhost:5555" in devices:
            devices.remove("localhost:5555")
        return devices
    except:
        return []

def parse_gradle(gradle_path):
    with open(gradle_path, 'r') as f:
        content = f.read()
    
    # Extract dimensions
    dims_match = re.search(r'flavorDimensions\s+(.*)', content)
    dimensions = []
    if dims_match:
        raw = dims_match.group(1)
        raw = re.sub(r'//.*', '', raw)
        dimensions = [d.strip().strip('"\'') for d in raw.split(',')]

    # Extract flavors
    flavors = {} 
    start_match = re.search(r'productFlavors\s*\{', content)
    if start_match:
        start_idx = start_match.end()
        brace_count = 1
        i = start_idx
        while i < len(content) and brace_count > 0:
            if content[i] == '{': brace_count += 1
            elif content[i] == '}': brace_count -= 1
            i += 1
        
        block_content = content[start_idx:i-1]
        flavor_defs = re.finditer(r'(\w+)\s*\{', block_content)
        
        for match in flavor_defs:
            name = match.group(1)
            f_start = match.end()
            f_brace = 1
            j = f_start
            while j < len(block_content) and f_brace > 0:
                if block_content[j] == '{': f_brace += 1
                elif block_content[j] == '}': f_brace -= 1
                j += 1
            
            f_body = block_content[f_start:j-1]
            dim_match = re.search(r'dimension\s+["\'](\w+)["\']', f_body)
            if dim_match:
                dim = dim_match.group(1)
                if dim not in flavors: flavors[dim] = []
                flavors[dim].append(name)
    
    return dimensions, flavors

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', choices=['build', 'run'], default='build', help='Action to perform')
    parser.add_argument('project_root', help='Project root directory')
    args = parser.parse_args()

    project_root = args.project_root
    app_dir = os.path.join(project_root, "app")
    gradle_file = os.path.join(app_dir, "build.gradle")

    if not os.path.exists(gradle_file):
        print("Error: build.gradle not found")
        sys.exit(1)

    dimensions, flavors = parse_gradle(gradle_file)
    devices = get_connected_devices()

    # Show GUI
    root = tk.Tk()
    config = {}
    
    def on_submit(res):
        nonlocal config
        config = res

    app = BuildDialog(root, dimensions, flavors, devices, on_submit)
    root.mainloop()

    if not app.result:
        print("Cancelled")
        sys.exit(1)

    res = app.result
    
    # Construct Task
    # assemble[Flavor1][Flavor2][BuildType]
    # Order of flavors must match dimensions order
    flavor_part = ""
    for dim in dimensions:
        val = res['flavors'].get(dim, "")
        if val:
            flavor_part += val[0].upper() + val[1:]
            
    build_type = res['build_type']
    task = f"assemble{flavor_part}{build_type}"
    
    print(f"Selected Task: {task}")
    print(f"Target Device: {res['device']}")

    # Execute Gradle
    gradlew = os.path.join(project_root, "gradlew")
    cmd = [gradlew, task]
    
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=project_root, check=True)
    except subprocess.CalledProcessError:
        print("Build Failed")
        sys.exit(1)

    if args.action == 'run':
        if not res['device']:
            print("No device selected for installation.")
            sys.exit(1)
            
        # Find APK
        # Find APK in specific flavor folder
        # Folder structure: app/build/outputs/apk/{flavor1}{Flavor2}.../{buildType}/
        folder_name = ""
        for i, dim in enumerate(dimensions):
            val = res['flavors'].get(dim, "")
            if val:
                if i == 0:
                    folder_name += val
                else:
                    folder_name += val[0].upper() + val[1:]
        
        bt_lower = build_type.lower()
        apk_dir = os.path.join(app_dir, "build", "outputs", "apk", folder_name, bt_lower)
        
        print(f"Looking for APK in: {apk_dir}")
        
        if not os.path.exists(apk_dir):
            # Fallback to recursive search if folder structure differs
            print("Specific folder not found, falling back to recursive search...")
            suffix = "debug.apk" if build_type == "Debug" else "release.apk"
            apk_pattern = os.path.join(app_dir, "build", "outputs", "apk", "**", f"*-{suffix}")
            apks = glob.glob(apk_pattern, recursive=True)
        else:
            apks = glob.glob(os.path.join(apk_dir, "*.apk"))

        # Filter out 'selected' and 'output-metadata.json'
        apks = [a for a in apks if "selected-" not in os.path.basename(a) and "output-metadata" not in os.path.basename(a)]
        
        if not apks:
            print(f"APK not found in {apk_dir}")
            sys.exit(1)
            
        latest_apk = max(apks, key=os.path.getctime)
        print(f"Installing: {latest_apk}")
        
        try:
            subprocess.run(["adb", "-s", res['device'], "install", "-r", latest_apk], check=True)
            
            # Get Package Name
            aapt_out = subprocess.check_output([AAPT, "dump", "badging", latest_apk], text=True)
            pkg_match = re.search(r"package: name='([^']+)'", aapt_out)
            if pkg_match:
                pkg = pkg_match.group(1)
                # Get Launchable Activity
                act_match = re.search(r"launchable-activity: name='([^']+)'", aapt_out)
                act = act_match.group(1) if act_match else f"{pkg}.MainActivity"
                
                print(f"Launching: {pkg}/{act}")
                subprocess.run(["adb", "-s", res['device'], "shell", "am", "start", "-n", f"{pkg}/{act}"], check=True)
                
        except Exception as e:
            print(f"Install/Launch failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
