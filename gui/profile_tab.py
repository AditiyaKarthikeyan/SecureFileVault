
import tkinter as tk
from tkinter import font, ttk
import datetime
from core import database

class ProfileTab(tk.Frame):
    def __init__(self, master, user_id, bg_color="#0c1e2f", 
                accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.user_id = user_id
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        # Load user data
        self.user_data = database.get_user_profile(user_id)
        self.user_activity = database.get_user_activity(user_id)
        
        # Main container
        main_container = tk.Frame(self, bg=bg_color)
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_container, bg=bg_color)
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_font = font.Font(family="Arial", size=24, weight="bold")
        tk.Label(header_frame, text="User Profile", font=header_font, 
                 bg=bg_color, fg=accent_color).pack(anchor="w")
        
        # Profile content container (2 columns layout)
        content_frame = tk.Frame(main_container, bg=bg_color)
        content_frame.pack(fill="both", expand=True)
        
        # User information card (left column)
        info_frame = tk.Frame(content_frame, bg="#163959", padx=20, pady=20, borderwidth=1, relief="solid")
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Profile header
        profile_header = tk.Frame(info_frame, bg="#163959")
        profile_header.pack(fill="x", pady=(0, 15))
        
        # Account icon/avatar
        avatar_frame = tk.Frame(profile_header, bg=accent_color, width=60, height=60)
        avatar_frame.pack(side="left", padx=(0, 15))
        avatar_frame.pack_propagate(False)
        
        avatar_text = self.user_data["username"][0].upper() if self.user_data["username"] else "U"
        tk.Label(avatar_frame, text=avatar_text, font=("Arial", 24, "bold"), 
                 bg=accent_color, fg="#ffffff").place(relx=0.5, rely=0.5, anchor="center")
        
        # User name and type
        user_header = tk.Frame(profile_header, bg="#163959")
        user_header.pack(side="left", fill="x", expand=True)
        
        name_font = font.Font(family="Arial", size=18, weight="bold")
        tk.Label(user_header, text=self.user_data["full_name"], font=name_font, 
                 bg="#163959", fg=text_color).pack(anchor="w")
        
        account_label = tk.Label(user_header, text=f"{self.user_data['account_type'].upper()} Account", 
                                font=("Arial", 10), bg=accent_color, fg=text_color, padx=10, pady=2)
        account_label.pack(anchor="w")
        
        # User details
        details_frame = tk.Frame(info_frame, bg="#163959")
        details_frame.pack(fill="x", pady=10)
        
        # Username
        detail_row = tk.Frame(details_frame, bg="#163959", pady=5)
        detail_row.pack(fill="x")
        tk.Label(detail_row, text="Username:", font=("Arial", 11, "bold"), 
                 bg="#163959", fg="#6c7983", width=15, anchor="w").pack(side="left")
        tk.Label(detail_row, text=self.user_data["username"], font=("Arial", 11), 
                 bg="#163959", fg=text_color).pack(side="left", padx=10)
        
        # Email
        detail_row = tk.Frame(details_frame, bg="#163959", pady=5)
        detail_row.pack(fill="x")
        tk.Label(detail_row, text="Email:", font=("Arial", 11, "bold"), 
                 bg="#163959", fg="#6c7983", width=15, anchor="w").pack(side="left")
        tk.Label(detail_row, text=self.user_data["email"], font=("Arial", 11), 
                 bg="#163959", fg=text_color).pack(side="left", padx=10)
        
        # Account created
        detail_row = tk.Frame(details_frame, bg="#163959", pady=5)
        detail_row.pack(fill="x")
        tk.Label(detail_row, text="Account created:", font=("Arial", 11, "bold"), 
                 bg="#163959", fg="#6c7983", width=15, anchor="w").pack(side="left")
        tk.Label(detail_row, text=self.user_data["created_at"], font=("Arial", 11), 
                 bg="#163959", fg=text_color).pack(side="left", padx=10)
        
        # Last login
        detail_row = tk.Frame(details_frame, bg="#163959", pady=5)
        detail_row.pack(fill="x")
        tk.Label(detail_row, text="Last login:", font=("Arial", 11, "bold"), 
                 bg="#163959", fg="#6c7983", width=15, anchor="w").pack(side="left")
        tk.Label(detail_row, text=self.user_data["last_login"] or "Never", font=("Arial", 11), 
                 bg="#163959", fg=text_color).pack(side="left", padx=10)
        
        # Security features
        security_frame = tk.Frame(info_frame, bg="#163959", pady=10)
        security_frame.pack(fill="x", pady=(20, 0))
        
        tk.Label(security_frame, text="Security Features", font=("Arial", 14, "bold"), 
                 bg="#163959", fg=accent_color).pack(anchor="w", pady=(0, 10))
        
        features = [
            ("Two-Factor Authentication", "Enabled"),
            ("Encryption", "AES-256"),
            ("Last Password Change", "Never")
        ]
        
        for feature, status in features:
            feature_row = tk.Frame(security_frame, bg="#163959", pady=5)
            feature_row.pack(fill="x")
            tk.Label(feature_row, text=feature, font=("Arial", 11), 
                     bg="#163959", fg=text_color, width=20, anchor="w").pack(side="left")
            
            status_color = accent_color if status == "Enabled" else text_color
            tk.Label(feature_row, text=status, font=("Arial", 11, "bold"), 
                     bg="#163959", fg=status_color).pack(side="left", padx=10)
        
        # Change password button
        def create_password_change_section(self):
            frame = tk.Frame(self, bg=self.bg_color, padx=10, pady=10)
            frame.pack(fill="x", pady=(10, 0))

            tk.Label(frame, text="Change Password", font=("Arial", 12, "bold"), 
                    bg=self.bg_color, fg=self.accent_color).pack(anchor="w")

            # Current Password
            tk.Label(frame, text="Current Password:", bg=self.bg_color, 
                    fg=self.text_color).pack(anchor="w", pady=(5, 0))
            self.current_pass = tk.Entry(frame, show="•", font=("Arial", 11), 
                                      bg="#214c78", fg=self.text_color, relief=tk.FLAT)
            self.current_pass.pack(fill="x", pady=(0, 5), ipady=5)

            # New Password
            tk.Label(frame, text="New Password:", bg=self.bg_color, 
                    fg=self.text_color).pack(anchor="w", pady=(5, 0))
            self.new_pass = tk.Entry(frame, show="•", font=("Arial", 11), 
                                   bg="#214c78", fg=self.text_color, relief=tk.FLAT)
            self.new_pass.pack(fill="x", pady=(0, 5), ipady=5)

            # Confirm New Password
            tk.Label(frame, text="Confirm New Password:", bg=self.bg_color, 
                    fg=self.text_color).pack(anchor="w", pady=(5, 0))
            self.confirm_pass = tk.Entry(frame, show="•", font=("Arial", 11), 
                                bg="#214c78", fg=self.text_color, relief=tk.FLAT)
            self.confirm_pass.pack(fill="x", pady=(0, 10), ipady=5)

            # Change Password Button with theme styling
            self.change_pass_btn = tk.Button(
                frame, 
                text="Change Password", 
                command=self.change_password,
                bg=self.accent_color,
                fg="#ffffff",
                font=("Arial", 11, "bold"),
                padx=15,
                pady=8,
                relief=tk.FLAT,
                activebackground="#319795",
                activeforeground="#ffffff"
            )
            self.change_pass_btn.pack(pady=(5, 0))
        
        # Activity log (right column)
        activity_frame = tk.Frame(content_frame, bg=bg_color)
        activity_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        tk.Label(activity_frame, text="Recent Activity", font=("Arial", 16, "bold"), 
                 bg=bg_color, fg=accent_color).pack(anchor="w", pady=(0, 10))
        
        # Activity table
        table_frame = tk.Frame(activity_frame, bg=bg_color)
        table_frame.pack(fill="both", expand=True)
        
        # Create Treeview for activity log
        style = ttk.Style()
        style.configure("Custom.Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color,
                        borderwidth=0)
        style.configure("Custom.Treeview.Heading", 
                        background="#214c78",
                        foreground=text_color,
                        relief="flat")
        style.map("Custom.Treeview.Heading",
                 background=[('active', '#214c78')])
        
        self.activity_tree = ttk.Treeview(table_frame, style="Custom.Treeview", 
                                         columns=("timestamp", "action", "details"), 
                                         show="headings",
                                         height=15)
        
        # Configure columns
        self.activity_tree.heading("timestamp", text="Time")
        self.activity_tree.heading("action", text="Activity")
        self.activity_tree.heading("details", text="Details")
        
        self.activity_tree.column("timestamp", width=150)
        self.activity_tree.column("action", width=150)
        self.activity_tree.column("details", width=300)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activity_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate activity data
        self.load_activity_data()
        
        # Refresh button
        refresh_button = tk.Button(activity_frame, text="Refresh", bg=button_color, 
                                 fg=text_color, font=("Arial", 10), padx=15, pady=5,
                                 relief=tk.FLAT, bd=0, cursor="hand2",
                                 command=self.load_activity_data)
        refresh_button.pack(anchor="e", pady=10)
    
    def load_activity_data(self):
        """Load and display user activity data"""
        # Clear existing data
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Refresh activity data
        self.user_activity = database.get_user_activity(self.user_id)
        
        # Insert into treeview
        for activity in self.user_activity:
            self.activity_tree.insert("", "end", values=(
                activity["timestamp"],
                activity["action"],
                activity["details"] or "-"
            ))
