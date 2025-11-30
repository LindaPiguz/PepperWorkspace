#!/usr/bin/env python3
import subprocess
import threading
import time
import sys
import signal
import os
import re

# Configuration
ADB_PATH = "/home/linda/Android/Sdk/platform-tools/adb"
PACKAGE = ""
DEVICE_SERIAL = ""
CURRENT_PID = None
STOP_EVENT = threading.Event()

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_active_config():
    """Loads configuration from .active_config file in the same directory."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(script_dir, ".active_config")
    
    config = {}
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"').strip("'")
                    config[key.strip()] = value
    return config

def find_device():
    """Detects the most likely target device."""
    try:
        cmd = [ADB_PATH, "devices"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        lines = res.stdout.strip().split('\n')[1:] # Skip header
        
        devices = []
        for line in lines:
            if "\tdevice" in line:
                devices.append(line.split('\t')[0])
        
        if not devices:
            return None
            
        # Priority 1: Emulator-5554 (Default Pepper Emulator)
        if "emulator-5554" in devices:
            return "emulator-5554"
            
        # Priority 2: Localhost:5555 (Alternative connection)
        if "localhost:5555" in devices:
            return "localhost:5555"
            
        # Priority 3: First available device
        return devices[0]
    except:
        return None

def get_pid():
    """Gets the PID of the package on the device."""
    if not DEVICE_SERIAL:
        return None
        
    try:
        # pidof returns PIDs separated by space. We take the last one (newest).
        cmd = [ADB_PATH, "-s", DEVICE_SERIAL, "shell", "pidof", PACKAGE]
        res = subprocess.run(cmd, capture_output=True, text=True)
        pids = res.stdout.strip().split()
        return pids[-1] if pids else None
    except:
        return None

def monitor_pid():
    """Background thread to monitor PID changes."""
    global CURRENT_PID
    
    while not STOP_EVENT.is_set():
        new_pid = get_pid()
        if new_pid != CURRENT_PID:
            if new_pid:
                if CURRENT_PID is None:
                    print(f"{Colors.GREEN}>>> App Started: {PACKAGE} (PID: {new_pid}) <<<{Colors.ENDC}")
                else:
                    print(f"{Colors.CYAN}>>> App Restarted: {PACKAGE} (PID: {new_pid}) <<<{Colors.ENDC}")
            else:
                if CURRENT_PID is not None:
                    print(f"{Colors.WARNING}>>> App Closed: {PACKAGE} <<<{Colors.ENDC}")
            CURRENT_PID = new_pid
        time.sleep(1)

def main():
    global PACKAGE, DEVICE_SERIAL
    
    # 1. Load Config
    config = load_active_config()
    
    # 2. Determine Package
    if len(sys.argv) > 1:
        PACKAGE = sys.argv[1]
    elif "PEPPER_PACKAGE" in config:
        PACKAGE = config["PEPPER_PACKAGE"]
    else:
        print(f"{Colors.FAIL}Error: No package name specified and none found in .active_config{Colors.ENDC}")
        print("Usage: monitor_logcat.py <package_name> [device_serial]")
        sys.exit(1)

    # 3. Determine Device
    if len(sys.argv) > 2:
        DEVICE_SERIAL = sys.argv[2]
    else:
        print(f"{Colors.BLUE}Auto-detecting device...{Colors.ENDC}")
        DEVICE_SERIAL = find_device()
        
    if not DEVICE_SERIAL:
        print(f"{Colors.FAIL}Error: No Android device found.{Colors.ENDC}")
        print("Please ensure the emulator is running or a robot is connected.")
        sys.exit(1)

    print(f"{Colors.HEADER}========================================{Colors.ENDC}", flush=True)
    print(f"{Colors.HEADER}   Logcat Monitor: {PACKAGE}{Colors.ENDC}", flush=True)
    print(f"{Colors.HEADER}   Device: {DEVICE_SERIAL}{Colors.ENDC}", flush=True)
    print(f"{Colors.HEADER}========================================{Colors.ENDC}", flush=True)
    # Plain text signal for problem matcher
    print(">>> MONITOR STARTED <<<", flush=True)

    # Start PID monitor
    t = threading.Thread(target=monitor_pid, daemon=True)
    t.start()
    
    # Start logcat process
    # We use -v color for colored output, and -v threadtime for timestamps
    process = subprocess.Popen(
        [ADB_PATH, "-s", DEVICE_SERIAL, "logcat", "-v", "color", "-v", "threadtime"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors='replace',
        bufsize=1
    )
    
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            # Filter Logic
            should_print = False
            
            if PACKAGE in line:
                should_print = True
            elif CURRENT_PID:
                if f" {CURRENT_PID} " in line or f":{CURRENT_PID} " in line or f" {CURRENT_PID}:" in line:
                    should_print = True
            
            if should_print:
                print(line, end='')
            
    except KeyboardInterrupt:
        print(f"\n{Colors.BLUE}Stopping monitor...{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Monitor Error: {e}{Colors.ENDC}")
    finally:
        STOP_EVENT.set()
        if process:
            process.terminate()

if __name__ == "__main__":
    main()
