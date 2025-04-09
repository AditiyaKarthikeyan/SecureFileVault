import tkinter as tk
from tkinter import font, ttk, messagebox
from core import database

class ProfileTab(tk.Frame):
    def __init__(self, master, user_id, on_change_password=None, bg_color="#0c1e2f", 
                accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.user_id = user_id
        self.on_change_password = on_change_password  # Store the callback
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        # Initialize password fields
        self.current_pass = None
        self.new_pass = None
        self.confirm_pass = None
        self.password_frame = None
        
        # Load user data
        self.load_user_data()
        self.setup_ui()

    def load_user_data(self):
        """Safely load user data"""
        try:
            self.user_data = database.get_user_profile(self.user_id)
            self.user_activity = database.get_user_activity(self.user_id)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load user data: {str(e)}")
            self.user_data = {
                "username": "Error",
                "full_name": "Error",
                "email": "Error",
                "created_at": "Error",
                "last_login": "Error",
                "account_type": "standard"
            }
            self.user_activity = []

    def setup_ui(self):
        """Setup the main UI components"""
        # Main container
        main_container = tk.Frame(self, bg=self.bg_color)
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_font = font.Font(family="Arial", size=24, weight="bold")
        tk.Label(header_frame, text="User Profile", font=header_font, 
                bg=self.bg_color, fg=self.accent_color).pack(anchor="w")

        # Content frame (2 columns)
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True)
        
        # Left column (user info + password change)
        left_column = tk.Frame(content_frame, bg=self.bg_color)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # User info card
        self.setup_user_info_card(left_column)
        
        # Password change trigger button
        change_pass_btn = tk.Button(
                left_column,
                text="🔑 Change Password",
                command=self.on_change_password if self.on_change_password else self.toggle_password_change,
                bg=self.accent_color,
                fg="#ffffff",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=8,
                relief=tk.FLAT,
                activebackground="#319795"
            )
        change_pass_btn.pack(pady=(20, 0), fill="x")
        
        # Right column (activity log)
        right_column = tk.Frame(content_frame, bg=self.bg_color)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Activity log header with refresh button
        self.setup_activity_header(right_column)
        
        # Activity table
        self.setup_activity_table(right_column)

    def toggle_password_change(self):
        """Toggle visibility of password change section"""
        if self.password_frame and self.password_frame.winfo_ismapped():
            self.password_frame.pack_forget()
        else:
            if not self.password_frame:
                self.create_password_change_section()
            self.password_frame.pack(fill="x", pady=(10, 0))

    def create_password_change_section(self):
        """Create password change form elements"""
        self.password_frame = tk.Frame(self, bg=self.bg_color, padx=10, pady=10)
        
        # Current Password
        tk.Label(self.password_frame, text="Current Password:", bg=self.bg_color, 
                fg=self.text_color, font=("Arial", 11)).pack(anchor="w", pady=(5, 0))
        self.current_pass = tk.Entry(self.password_frame, show="•", font=("Arial", 11), 
                                   bg="#214c78", fg=self.text_color, relief=tk.FLAT)
        self.current_pass.pack(fill="x", ipady=5, pady=(0, 10))
        
        # New Password
        tk.Label(self.password_frame, text="New Password:", bg=self.bg_color, 
                fg=self.text_color, font=("Arial", 11)).pack(anchor="w", pady=(5, 0))
        self.new_pass = tk.Entry(self.password_frame, show="•", font=("Arial", 11), 
                               bg="#214c78", fg=self.text_color, relief=tk.FLAT)
        self.new_pass.pack(fill="x", ipady=5, pady=(0, 10))
        
        # Confirm Password
        tk.Label(self.password_frame, text="Confirm New Password:", bg=self.bg_color, 
                fg=self.text_color, font=("Arial", 11)).pack(anchor="w", pady=(5, 0))
        self.confirm_pass = tk.Entry(self.password_frame, show="•", font=("Arial", 11), 
                                   bg="#214c78", fg=self.text_color, relief=tk.FLAT)
        self.confirm_pass.pack(fill="x", ipady=5, pady=(0, 10))
        
        # Change button
        change_btn = tk.Button(
            self.password_frame,
            text="Change Password",
            command=self.change_password,
            bg=self.accent_color,
            fg="#ffffff",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5,
            relief=tk.FLAT,
            activebackground="#319795"
        )
        change_btn.pack(fill="x", pady=(5, 0))

    def setup_user_info_card(self, parent):
        """Setup user information card"""
        info_frame = tk.Frame(parent, bg="#163959", padx=20, pady=20, borderwidth=1, relief="solid")
        info_frame.pack(fill="both", expand=True)
        
        # Profile header
        profile_header = tk.Frame(info_frame, bg="#163959")
        profile_header.pack(fill="x", pady=(0, 15))
        
        # Avatar
        avatar_frame = tk.Frame(profile_header, bg=self.accent_color, width=60, height=60)
        avatar_frame.pack(side="left", padx=(0, 15))
        avatar_frame.pack_propagate(False)
        
        avatar_text = self.user_data["username"][0].upper() if self.user_data["username"] else "U"
        tk.Label(avatar_frame, text=avatar_text, font=("Arial", 24, "bold"), 
                bg=self.accent_color, fg="#ffffff").place(relx=0.5, rely=0.5, anchor="center")
        
        # User name and type
        user_header = tk.Frame(profile_header, bg="#163959")
        user_header.pack(side="left", fill="x", expand=True)
        
        name_font = font.Font(family="Arial", size=18, weight="bold")
        tk.Label(user_header, text=self.user_data["full_name"], font=name_font, 
                bg="#163959", fg=self.text_color).pack(anchor="w")
        
        account_label = tk.Label(user_header, 
                               text=f"{self.user_data['account_type'].upper()} Account", 
                               font=("Arial", 10), 
                               bg=self.accent_color, 
                               fg=self.text_color, 
                               padx=10, 
                               pady=2)
        account_label.pack(anchor="w")

        # User details
        details_frame = tk.Frame(info_frame, bg="#163959")
        details_frame.pack(fill="x", pady=10)
        
        details = [
            ("Username:", self.user_data["username"]),
            ("Email:", self.user_data["email"]),
            ("Account created:", self.user_data["created_at"]),
            ("Last login:", self.user_data.get("last_login", "Never"))
        ]
        
        for label, value in details:
            row = tk.Frame(details_frame, bg="#163959", pady=5)
            row.pack(fill="x")
            tk.Label(row, text=label, font=("Arial", 11, "bold"), 
                    bg="#163959", fg="#6c7983", width=15, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Arial", 11), 
                    bg="#163959", fg=self.text_color).pack(side="left", padx=10)

        # Security features
        security_frame = tk.Frame(info_frame, bg="#163959", pady=10)
        security_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(security_frame, text="Security Features", font=("Arial", 14, "bold"), 
                bg="#163959", fg=self.accent_color).pack(anchor="w", pady=(0, 10))
        
        features = [
            ("Two-Factor Authentication", "Enabled"),
            ("Encryption", "AES-256"),
            ("Last Password Change", "Never")
        ]
        
        for feature, status in features:
            row = tk.Frame(security_frame, bg="#163959", pady=5)
            row.pack(fill="x")
            tk.Label(row, text=feature, font=("Arial", 11), 
                    bg="#163959", fg=self.text_color, width=20, anchor="w").pack(side="left")
            
            status_color = self.accent_color if status == "Enabled" else self.text_color
            tk.Label(row, text=status, font=("Arial", 11, "bold"), 
                    bg="#163959", fg=status_color).pack(side="left", padx=10)

    def setup_activity_header(self, parent):
        """Setup activity log header with refresh button"""
        header_frame = tk.Frame(parent, bg=self.bg_color)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        tk.Label(header_frame, text="Recent Activity", font=("Arial", 16, "bold"), 
                bg=self.bg_color, fg=self.accent_color).pack(side="left", anchor="w")
        
        # Refresh button
        refresh_button = tk.Button(
            header_frame,
            text="🔄 Refresh", 
            command=self.load_activity_data,
            bg=self.button_color,
            fg=self.text_color,
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5,
            relief=tk.FLAT,
            activebackground="#102a43",
            activeforeground="#ffffff"
        )
        refresh_button.pack(side="right")

    def setup_activity_table(self, parent):
        """Setup activity log table"""
        table_frame = tk.Frame(parent, bg=self.bg_color)
        table_frame.pack(fill="both", expand=True)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                      background=self.bg_color, 
                      foreground=self.text_color,
                      fieldbackground=self.bg_color,
                      borderwidth=0)
        style.configure("Custom.Treeview.Heading", 
                       background="#214c78",
                       foreground=self.text_color,
                       font=("Arial", 10, "bold"),
                       relief="flat")
        
        self.activity_tree = ttk.Treeview(
            table_frame,
            style="Custom.Treeview",
            columns=("timestamp", "action", "details"),
            show="headings",
            height=15
        )
        
        # Configure columns
        self.activity_tree.heading("timestamp", text="Time")
        self.activity_tree.heading("action", text="Activity")
        self.activity_tree.heading("details", text="Details")
        
        self.activity_tree.column("timestamp", width=150, anchor="w")
        self.activity_tree.column("action", width=150, anchor="w")
        self.activity_tree.column("details", width=300, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load initial data
        self.load_activity_data()

    def load_activity_data(self):
        """Load activity data into treeview"""
        try:
            self.activity_tree.delete(*self.activity_tree.get_children())
            activities = database.get_user_activity(self.user_id)
            for activity in activities:
                self.activity_tree.insert("", "end", values=(
                    activity.get("timestamp", ""),
                    activity.get("action", ""),
                    activity.get("details", "-")
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load activity: {str(e)}")

    def change_password(self):
        """Handle password change logic"""
        current = self.current_pass.get()
        new = self.new_pass.get()
        confirm = self.confirm_pass.get()
        
        # Validation
        if not all([current, new, confirm]):
            messagebox.showerror("Error", "All fields are required")
            return
            
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return
            
        if len(new) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
            
        # Verify current password and update
        if database.update_password(self.user_id, current, new):
            messagebox.showinfo("Success", "Password changed successfully")
            self.toggle_password_change()
        else:
            messagebox.showerror("Error", "Failed to change password")
