
import tkinter as tk
from tkinter import font, ttk
import os
from datetime import datetime

LOG_FILE = "assets/logs/activity.log"

class LogTab(tk.Frame):
    def __init__(self, master, bg_color="#0c1e2f", accent_color="#38b2ac", 
                 text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        self.create_ui()
        self.load_logs()
        
    def create_ui(self):
        # Container
        main_container = tk.Frame(self, bg=self.bg_color, padx=15, pady=15)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        header_font = font.Font(family="Arial", size=16, weight="bold")
        tk.Label(header_frame, text="📝 Security Logs", font=header_font,
                bg=self.bg_color, fg=self.accent_color).pack(side=tk.LEFT)
        
        # Control panel
        control_frame = tk.Frame(main_container, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search box
        search_container = tk.Frame(control_frame, bg=self.bg_color)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(search_container, text="Filter:", bg=self.bg_color, 
                fg=self.text_color).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_container, bg="#214c78", fg=self.text_color,
                                    insertbackground=self.text_color, relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_logs)
        
        # Buttons
        button_container = tk.Frame(control_frame, bg=self.bg_color)
        button_container.pack(side=tk.RIGHT)
        
        button_style = {
            "font": ("Arial", 10),
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 6
        }
        
        tk.Button(button_container, text="🔄 Refresh", bg=self.button_color,
                 fg=self.text_color, command=self.load_logs,
                 activebackground=self.accent_color, **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_container, text="📤 Export", bg=self.button_color,
                 fg=self.text_color, command=self.export_logs,
                 activebackground=self.accent_color, **button_style).pack(side=tk.LEFT, padx=5)
        
        # Advanced options frame
        options_frame = tk.Frame(main_container, bg=self.bg_color)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date filter
        date_frame = tk.Frame(options_frame, bg=self.bg_color)
        date_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Label(date_frame, text="Date:", bg=self.bg_color, 
                fg=self.text_color).pack(side=tk.LEFT, padx=2)
        
        self.date_var = tk.StringVar(value="All")
        date_options = ["All", "Today", "Last 3 Days", "Last Week"]
        date_menu = ttk.Combobox(date_frame, textvariable=self.date_var, 
                                values=date_options, width=10, state="readonly")
        date_menu.pack(side=tk.LEFT)
        date_menu.bind("<<ComboboxSelected>>", self.filter_logs)
        
        # User filter
        user_frame = tk.Frame(options_frame, bg=self.bg_color)
        user_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(user_frame, text="User:", bg=self.bg_color, 
                fg=self.text_color).pack(side=tk.LEFT, padx=2)
        
        self.user_var = tk.StringVar(value="All")
        user_menu = ttk.Combobox(user_frame, textvariable=self.user_var, 
                                values=["All", "admin"], width=10, state="readonly")
        user_menu.pack(side=tk.LEFT)
        user_menu.bind("<<ComboboxSelected>>", self.filter_logs)
        
        # Event type filter
        event_frame = tk.Frame(options_frame, bg=self.bg_color)
        event_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(event_frame, text="Event:", bg=self.bg_color, 
                fg=self.text_color).pack(side=tk.LEFT, padx=2)
        
        self.event_var = tk.StringVar(value="All")
        event_menu = ttk.Combobox(event_frame, textvariable=self.event_var, 
                                 values=["All", "Login", "File", "Firewall"], width=10, state="readonly")
        event_menu.pack(side=tk.LEFT)
        event_menu.bind("<<ComboboxSelected>>", self.filter_logs)
        
        # Log display area
        self.log_frame = tk.Frame(main_container, bg=self.bg_color)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for logs
        columns = ("timestamp", "user", "action")
        self.log_tree = ttk.Treeview(self.log_frame, columns=columns, show="headings")
        
        # Configure column headings
        self.log_tree.heading("timestamp", text="Timestamp")
        self.log_tree.heading("user", text="User")
        self.log_tree.heading("action", text="Action")
        
        # Configure column widths
        self.log_tree.column("timestamp", width=180)
        self.log_tree.column("user", width=100)
        self.log_tree.column("action", width=400)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#214c78", 
                        foreground=self.text_color, 
                        rowheight=25,
                        fieldbackground="#214c78")
        style.map("Treeview", background=[("selected", self.accent_color)])
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.log_frame, orient="vertical", command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = tk.Label(main_container, textvariable=self.status_var, 
                             bg="#214c78", fg=self.text_color, anchor="w", 
                             relief=tk.FLAT, padx=10, pady=5)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
    def load_logs(self):
        # Clear existing logs
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                log_lines = f.readlines()
                
            log_entries = []
            for line in log_lines:
                line = line.strip()
                if line:
                    # Parse the log line: [timestamp] [username] action
                    try:
                        timestamp_end = line.find("]", 1)
                        timestamp = line[1:timestamp_end]
                        
                        username_start = line.find("[", timestamp_end) + 1
                        username_end = line.find("]", username_start)
                        username = line[username_start:username_end]
                        
                        action = line[username_end+2:]
                        
                        # Insert into treeview
                        self.log_tree.insert("", tk.END, values=(timestamp, username, action))
                    except:
                        # If parsing fails, just add the full line as action
                        self.log_tree.insert("", tk.END, values=("", "", line))
                
            entry_count = len(log_lines)
            self.status_var.set(f"Displaying {entry_count} log entries")
        else:
            self.status_var.set("No log file found. Events will be logged when they occur.")
        
        self.filter_logs()
            
    def filter_logs(self, event=None):
        # Get filter values
        search_text = self.search_entry.get().lower()
        date_filter = self.date_var.get()
        user_filter = self.user_var.get()
        event_filter = self.event_var.get()
        
        # Show all items first
        for item in self.log_tree.get_children():
            self.log_tree.item(item, tags="")
            
        visible_count = 0
        filtered_items = []
        
        # Apply filters
        for item in self.log_tree.get_children():
            values = self.log_tree.item(item)["values"]
            timestamp, username, action = values[0], values[1], values[2]
            
            show_item = True
            
            # Text search filter
            if search_text and not (search_text in str(timestamp).lower() or 
                                   search_text in str(username).lower() or 
                                   search_text in str(action).lower()):
                show_item = False
                
            # Date filter
            if date_filter != "All" and timestamp:
                try:
                    log_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    current_date = datetime.now()
                    
                    if date_filter == "Today":
                        if log_date.date() != current_date.date():
                            show_item = False
                    elif date_filter == "Last 3 Days":
                        if (current_date.date() - log_date.date()).days > 3:
                            show_item = False
                    elif date_filter == "Last Week":
                        if (current_date.date() - log_date.date()).days > 7:
                            show_item = False
                except:
                    # If date parsing fails, don't filter by date
                    pass
                    
            # User filter
            if user_filter != "All" and username != user_filter:
                show_item = False
                
            # Event filter
            if event_filter != "All":
                if event_filter == "Login" and "login" not in str(action).lower():
                    show_item = False
                elif event_filter == "File" and "file" not in str(action).lower():
                    show_item = False
                elif event_filter == "Firewall" and "firewall" not in str(action).lower():
                    show_item = False
                    
            # Apply visibility
            if show_item:
                visible_count += 1
            else:
                filtered_items.append(item)
                
        # Hide filtered items
        for item in filtered_items:
            self.log_tree.detach(item)
            
        # Update status
        total_count = len(self.log_tree.get_children())
        filtered_count = len(filtered_items)
        self.status_var.set(f"Displaying {visible_count} of {total_count} log entries")
        
    def export_logs(self):
        import datetime
        import shutil
        
        # Create export filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = f"logs_export_{timestamp}.txt"
        
        if os.path.exists(LOG_FILE):
            try:
                # Copy the log file
                shutil.copy2(LOG_FILE, export_file)
                self.status_var.set(f"Logs exported to {export_file}")
            except Exception as e:
                self.status_var.set(f"Export failed: {str(e)}")
        else:
            self.status_var.set("No logs to export")
