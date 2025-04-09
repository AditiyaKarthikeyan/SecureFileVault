
import tkinter as tk
from tkinter import ttk, messagebox
from core import database, logger

class AdminTab(tk.Frame):
    def __init__(self, master, user_id, bg_color="#0c1e2f", 
                 accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.user_id = user_id
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        # Get the current user profile
        self.user_profile = database.get_user_profile(user_id)
        
        # Check if user is admin
        if self.user_profile['account_type'] != 'admin':
            tk.Label(
                self, 
                text="Access Denied: Admin privileges required", 
                font=("Arial", 16, "bold"), 
                bg=bg_color, 
                fg="#e74c3c"
            ).pack(expand=True, pady=50)
            return
        
        # Title
        title = tk.Label(
            self, 
            text="User Access Control", 
            font=("Arial", 18, "bold"), 
            bg=bg_color, 
            fg=accent_color
        )
        title.pack(pady=(20, 10))
        
        # Description
        description = tk.Label(
            self, 
            text="Manage user permissions for firewall and logs access", 
            font=("Arial", 12), 
            bg=bg_color, 
            fg=text_color
        )
        description.pack(pady=(0, 20))
        
        # Create main container
        container = tk.Frame(self, bg=bg_color)
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create a frame for the user list with a scrollbar
        list_frame = tk.Frame(container, bg=bg_color)
        list_frame.pack(fill="both", expand=True)
        
        # Create treeview for user list
        columns = ("username", "full_name", "email", "firewall", "logs")
        self.user_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.user_tree.heading("username", text="Username")
        self.user_tree.heading("full_name", text="Full Name")
        self.user_tree.heading("email", text="Email")
        self.user_tree.heading("firewall", text="Firewall Access")
        self.user_tree.heading("logs", text="Logs Access")
        
        # Define column widths
        self.user_tree.column("username", width=150)
        self.user_tree.column("full_name", width=200)
        self.user_tree.column("email", width=250)
        self.user_tree.column("firewall", width=100)
        self.user_tree.column("logs", width=100)
        
        # Add scrollbar to the treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.user_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind select event
        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_select)
        
        # Create a form for editing permissions
        form_frame = tk.Frame(container, bg=bg_color, padx=20, pady=10)
        form_frame.pack(fill="x", pady=20)
        
        # Selected user info
        self.selected_label = tk.Label(
            form_frame, 
            text="Select a user to edit permissions", 
            font=("Arial", 12, "bold"), 
            bg=bg_color, 
            fg=text_color
        )
        self.selected_label.pack(anchor="w", pady=(0, 15))
        
        # Firewall access checkbox
        checkbox_frame = tk.Frame(form_frame, bg=bg_color)
        checkbox_frame.pack(fill="x", pady=5)
        
        self.firewall_var = tk.BooleanVar()
        self.firewall_check = tk.Checkbutton(
            checkbox_frame, 
            text="Allow Firewall Access", 
            variable=self.firewall_var,
            font=("Arial", 11),
            bg=bg_color,
            fg=text_color,
            selectcolor=button_color,
            activebackground=bg_color,
            activeforeground=text_color
        )
        self.firewall_check.pack(side="left", padx=(0, 20))
        
        # Logs access checkbox
        self.logs_var = tk.BooleanVar()
        self.logs_check = tk.Checkbutton(
            checkbox_frame, 
            text="Allow Logs Access", 
            variable=self.logs_var,
            font=("Arial", 11),
            bg=bg_color,
            fg=text_color,
            selectcolor=button_color,
            activebackground=bg_color,
            activeforeground=text_color
        )
        self.logs_check.pack(side="left")
        
        # Save button
        self.save_button = tk.Button(
            form_frame,
            text="Save Permissions",
            command=self._save_permissions,
            bg=accent_color,
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=15,
            pady=5,
            state="disabled"
        )
        self.save_button.pack(pady=15)
        
        # Status label
        self.status_label = tk.Label(
            form_frame,
            text="",
            font=("Arial", 10),
            bg=bg_color,
            fg="#2ecc71"
        )
        self.status_label.pack()
        
        # Refresh button
        refresh_button = tk.Button(
            container,
            text="Refresh User List",
            command=self._load_users,
            bg=button_color,
            fg=text_color,
            font=("Arial", 10),
            padx=10,
            pady=3
        )
        refresh_button.pack(pady=10)
        
        # Load users initially
        self._load_users()
        
        # Store the selected user id
        self.selected_user_id = None
    
    def _load_users(self):
        """Load users and display in treeview"""
        # Clear existing items
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Get all users
        users = database.get_all_users()
        
        # Display users
        for user in users:
            # Skip current admin user
            if user['id'] == self.user_id:
                continue
                
            # Format access as Yes/No
            firewall_access = "Yes" if user['can_access_firewall'] else "No"
            logs_access = "Yes" if user['can_access_logs'] else "No"
            
            self.user_tree.insert(
                "", 
                "end", 
                iid=user['id'],
                values=(
                    user['username'], 
                    user['full_name'], 
                    user['email'], 
                    firewall_access, 
                    logs_access
                )
            )
    
    def _on_user_select(self, event):
        """Handle user selection in treeview"""
        # Get selected item
        selected_items = self.user_tree.selection()
        if not selected_items:
            return
            
        # Get user id
        self.selected_user_id = selected_items[0]
        
        # Get user details
        selected = self.user_tree.item(self.selected_user_id)
        username = selected['values'][0]
        
        # Update selected label
        self.selected_label.config(text=f"Editing permissions for: {username}")
        
        # Enable save button
        self.save_button.config(state="normal")
        
        # Set checkboxes based on current permissions
        firewall_access = selected['values'][3] == "Yes"
        logs_access = selected['values'][4] == "Yes"
        
        self.firewall_var.set(firewall_access)
        self.logs_var.set(logs_access)
        
    def _save_permissions(self):
        """Save updated permissions"""
        if not self.selected_user_id:
            return
            
        # Clear status
        self.status_label.config(text="")
        
        # Get new permission values
        firewall_access = self.firewall_var.get()
        logs_access = self.logs_var.get()
        
        # Update permissions
        success = database.update_user_permissions(
            self.selected_user_id,
            firewall_access,
            logs_access
        )
        
        if success:
            # Update the display
            selected = self.user_tree.item(self.selected_user_id)
            values = list(selected['values'])
            values[3] = "Yes" if firewall_access else "No"
            values[4] = "Yes" if logs_access else "No"
            
            self.user_tree.item(self.selected_user_id, values=values)
            
            # Show success message
            self.status_label.config(text="Permissions updated successfully")
            
            # Log activity
            username = selected['values'][0]
            database.log_user_activity(
                self.user_id,
                "User Permissions Updated",
                f"Updated permissions for user: {username}"
            )
            logger.log_event(f"Admin updated permissions for user: {username}")
        else:
            # Show error
            self.status_label.config(text="Failed to update permissions", fg="#e74c3c")
