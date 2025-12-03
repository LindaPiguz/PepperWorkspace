#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

HISTORY_FILE = os.path.expanduser("~/.pepper_ip_history")

class IPSelectionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect to Pepper")
        self.geometry("400x350")
        self.resizable(False, False)

        # Result storage
        self.selected_ip = None
        self.is_new = False

        # UI Setup
        self._create_widgets()
        self._load_history()

        # Center window
        self.eval('tk::PlaceWindow . center')

    def _create_widgets(self):
        # Header
        header = ttk.Label(self, text="Select a Robot or Enter New IP", font=("Arial", 12, "bold"))
        header.pack(pady=10)

        # Listbox for History
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        self.listbox = tk.Listbox(list_frame, height=8, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.bind('<<ListboxSelect>>', self._on_select)

        # New IP Entry
        entry_frame = ttk.LabelFrame(self, text="New Connection")
        entry_frame.pack(fill=tk.X, padx=20, pady=10)

        self.ip_var = tk.StringVar(value="192.168.")
        self.ip_entry = ttk.Entry(entry_frame, textvariable=self.ip_var, font=("Arial", 10))
        self.ip_entry.pack(fill=tk.X, padx=10, pady=10)
        
        # Bind entry click/focus to clear list selection
        self.ip_entry.bind("<FocusIn>", self._on_entry_focus)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Connect", command=self._connect).pack(side=tk.RIGHT)

    def _load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r') as f:
                    ips = [line.strip() for line in f if line.strip()]
                for ip in ips:
                    self.listbox.insert(tk.END, ip)
            except Exception as e:
                print(f"Error loading history: {e}", file=sys.stderr)

    def _on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            ip = self.listbox.get(selection[0])
            self.ip_var.set(ip)
            self.is_new = False

    def _on_entry_focus(self, event):
        self.listbox.selection_clear(0, tk.END)
        self.is_new = True

    def _connect(self):
        ip = self.ip_var.get().strip()
        if not ip or ip == "192.168.":
            messagebox.showwarning("Invalid IP", "Please enter a valid IP address.")
            return

        # Check if this IP is already in history to determine "is_new" flag accurately
        # If user typed an IP that is already in history, treat it as existing (no save prompt needed)
        history_ips = self.listbox.get(0, tk.END)
        if ip in history_ips:
            self.is_new = False
        else:
            # If the user clicked the list, is_new is False.
            # If they typed a new IP, is_new is True.
            # The focus handler sets is_new=True, but let's double check.
            pass 

        print(f"{ip}|{str(self.is_new).lower()}") # Output format: IP|is_new
        self.destroy()

    def _cancel(self):
        sys.exit(1)

if __name__ == "__main__":
    app = IPSelectionApp()
    app.mainloop()
