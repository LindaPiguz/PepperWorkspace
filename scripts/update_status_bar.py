#!/usr/bin/env python3
import sys
import json
import os
import sys
import re
import tempfile
import shutil

# Resolve workspace file path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_FILE = os.path.join(SCRIPT_DIR, "../PepperAndroid.code-workspace")

def update_status(status_text, color=None):
    try:
        with open(WORKSPACE_FILE, 'r') as f:
            content = f.read()

        # Find the block: { ... "command": "./pepper_menu.sh" ... }
        # We need to match the whole object.
        # Pattern: { [^}]+ "command": "./pepper_menu.sh" [^}]+ }
        
        pattern = r'(\{[^{}]*"command": "\./pepper_menu\.sh"[^{}]*\})'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            block = match.group(1)
            new_block = block
            
            # Update Name
            new_block = re.sub(r'"name": "[^"]+"', f'"name": "{status_text}"', new_block)
            
            # Update Color
            if color:
                if '"color":' in new_block:
                    new_block = re.sub(r'"color": "[^"]+"', f'"color": "{color}"', new_block)
                else:
                    # Insert color after name
                    new_block = re.sub(r'("name": "[^"]+",)', f'\\1\n\t\t\t"color": "{color}",', new_block)
            
            content = content.replace(block, new_block)
            
            # Atomic write to ensure VS Code detects the change
            # Create a temp file in the same directory to ensure atomic move
            dir_name = os.path.dirname(WORKSPACE_FILE)
            with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tf:
                tf.write(content)
                temp_name = tf.name
            
            # Replace the original file
            os.replace(temp_name, WORKSPACE_FILE)
            
            print(f"Updated status to: {status_text} (Color: {color})")
            return

        print("Could not find status button block.")
        
    except Exception as e:
        print(f"Failed to update status: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: update_status_bar.py <status_text> [color]")
        sys.exit(1)
    
    status = sys.argv[1]
    col = sys.argv[2] if len(sys.argv) > 2 else None
        
    update_status(status, col)
