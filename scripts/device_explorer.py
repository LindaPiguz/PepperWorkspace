#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os

class DeviceExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pepper Device Explorer")
        self.geometry("800x600")

        self.current_path = "/sdcard"
        self.history = []

        # UI Layout
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(top_frame, text="Up", command=self.go_up).pack(side=tk.LEFT)
        self.path_label = ttk.Label(top_frame, text=self.current_path, font=("Consolas", 10))
        self.path_label.pack(side=tk.LEFT, padx=10)
        
        # Search UI
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        ttk.Button(top_frame, text="Find", command=self.perform_search).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT)
        
        ttk.Button(top_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT)

        # Treeview for files
        self.tree = ttk.Treeview(self, columns=("Size", "Date"), selectmode="browse")
        self.tree.heading("#0", text="Name", anchor=tk.W)
        self.tree.heading("Size", text="Size", anchor=tk.W)
        self.tree.heading("Date", text="Date", anchor=tk.W)
        self.tree.column("#0", width=400)
        self.tree.column("Size", width=100)
        self.tree.column("Date", width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Bottom Actions
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(bottom_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT, padx=5)

        self.refresh()

    def run_adb(self, cmd):
        # Force target emulator-5554 if multiple devices are present
        # A better solution would be a device selector, but for this workspace, 5554 is standard.
        if "adb " in cmd and "-s " not in cmd:
            cmd = cmd.replace("adb ", "adb -s emulator-5554 ")
            
        try:
            return subprocess.check_output(cmd, shell=True, text=True)
        except subprocess.CalledProcessError as e:
            return None

    def perform_search(self):
        query = self.search_var.get().strip()
        if not query:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.path_label.config(text=f"Searching for '{query}' in {self.current_path}...")
        self.update_idletasks()
        
        # Use find command
        # -L to follow symlinks? Maybe not to avoid loops.
        cmd = f"adb -s emulator-5554 shell find \"{self.current_path}\" -name \"*{query}*\""
        output = self.run_adb(cmd)
        
        if output:
            lines = output.split('\n')
            for line in lines:
                path = line.strip()
                if not path: continue
                
                # Check if permission denied or other error in output
                if "Permission denied" in path: continue
                
                # Get details for this file to look nice
                # This might be slow for many results, so maybe just show path
                # Let's just show the path relative to current_path or full path
                
                name = os.path.basename(path)
                full_path = path
                
                # Determine if dir (simple heuristic: find output doesn't tell us easily without ls -ld)
                # We'll assume file for icon unless we check. 
                # Let's just show a generic search icon 🔍
                
                self.tree.insert("", "end", text=f"🔍 {full_path}", values=("-", "-"), tags=("search_result",))
        
        self.path_label.config(text=f"Search results for '{query}'")

    def clear_search(self):
        self.search_var.set("")
        self.refresh()

    def refresh(self):
        self.path_label.config(text=self.current_path)
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Use ls -l to get details. 
        # Note: Android's ls -l output can vary (missing size for dirs).
        # We append a trailing slash to ensure we list the *contents* of the directory,
        # especially important for symlinks like /sdcard.
        list_path = self.current_path
        if not list_path.endswith('/'):
            list_path += '/'
            
        cmd = f"adb -s emulator-5554 shell ls -l \"{list_path}\""
        output = self.run_adb(cmd)
        
        if output:
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith("total"): continue
                
                parts = line.split()
                if len(parts) < 6: continue
                
                # Parse based on Date/Time position
                # Format usually: perms owner group [size] date time name
                # We look for the date pattern YYYY-MM-DD
                
                date_idx = -1
                for i, part in enumerate(parts):
                    if len(part) == 10 and part[4] == '-' and part[7] == '-':
                        date_idx = i
                        break
                
                if date_idx != -1 and date_idx + 2 < len(parts):
                    perms = parts[0]
                    date = parts[date_idx]
                    time = parts[date_idx+1]
                    name = " ".join(parts[date_idx+2:])
                    
                    # Size is usually before date
                    size = "-"
                    if date_idx > 0:
                        potential_size = parts[date_idx-1]
                        if potential_size.isdigit():
                            size = potential_size
                    
                    is_dir = perms.startswith('d')
                    
                    # Icon prefix
                    icon = "📁 " if is_dir else "📄 "
                    
                    # Insert into tree
                    self.tree.insert("", "end", text=f"{icon}{name}", values=(size, f"{date} {time}"), tags=("dir" if is_dir else "file",))
                else:
                    # Fallback for unexpected formats (just show name if possible)
                    # Assuming last part is name
                    name = parts[-1]
                    self.tree.insert("", "end", text=f"❓ {name}", values=("?", "?"), tags=("file",))

    def go_up(self):
        if self.current_path == "/": return
        self.current_path = os.path.dirname(self.current_path.rstrip('/'))
        if not self.current_path: self.current_path = "/"
        self.refresh()

    def on_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
            
        item_id = selection[0]
        item_text = self.tree.item(item_id, "text")
        tags = self.tree.item(item_id, "tags")

        if "search_result" in tags:
            # It's a full path
            full_path = item_text[2:] # Remove icon
            # If it's a directory, go there. If file, open it.
            # We need to check if it's a dir. Naive check: does it have an extension?
            # Better: check our tree values or just try to open it.
            # For now, let's assume if it has no extension it's a dir, or try to cd into it.
            # Actually, let's just use the parent dir logic for navigation safety, 
            # BUT if the user wants to open the file, we should try that.
            
            # Let's try to determine if it is a file or dir based on the icon we set
            if "📁" in item_text:
                # Directory -> Go to it
                self.current_path = full_path
                self.clear_search()
                return
            else:
                # File -> Open it
                self.open_file(full_path)
                return

        # Normal view
        name = item_text[2:] 
        
        if "dir" in tags:
            if self.current_path == "/":
                self.current_path += name
            else:
                self.current_path = f"{self.current_path}/{name}".replace("//", "/")
            
            # Remove trailing slash if present from ls -p
            if self.current_path.endswith('/'):
                self.current_path = self.current_path[:-1]
                
            self.refresh()
        else:
            # It's a file -> Open it
            full_path = f"{self.current_path}/{name}".replace("//", "/")
            self.open_file(full_path)

    def open_file(self, remote_path):
        # Download to a temp folder and open
        import tempfile
        import shutil
        
        filename = os.path.basename(remote_path)
        temp_dir = os.path.join(tempfile.gettempdir(), "Raven_Temp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        local_path = os.path.join(temp_dir, filename)
        
        # Force target emulator-5554
        cmd = f"adb -s emulator-5554 pull \"{remote_path}\" \"{local_path}\""
        
        try:
            subprocess.check_call(cmd, shell=True)
            print(f"Downloaded to {local_path}")
            if os.name == 'posix':
                subprocess.call(['xdg-open', local_path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected: return
        
        item_text = self.tree.item(selected[0], "text")
        tags = self.tree.item(selected[0], "tags")
        
        if "search_result" in tags:
            remote_path = item_text[2:]
            name = os.path.basename(remote_path)
        else:
            name = item_text[2:].rstrip('/') # Remove icon and trailing slash
            remote_path = f"{self.current_path}/{name}".replace("//", "/")
            
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{name}'?"):
            cmd = f"adb -s emulator-5554 shell rm -rf \"{remote_path}\""
            try:
                subprocess.check_call(cmd, shell=True)
                # Refresh
                if "search_result" in tags:
                    self.perform_search()
                else:
                    self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")

if __name__ == "__main__":
    app = DeviceExplorer()
    app.mainloop()
