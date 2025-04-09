import tkinter as tk
from tkinter import ttk, font
from gui import login_tab, register_tab, vault_tab, firewall_tab, log_tab, profile_tab, admin_tab, file_sharing_tab, change_password_tab
import os
from core import database

class SecureFileVaultApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SecureFileVault")
        self.geometry("900x650")
        self.minsize(800, 600)

        self.bg_color = "#0c1e2f"
        self.accent_color = "#38b2ac"
        self.text_color = "#ffffff"
        self.button_color = "#163959"

        self.configure(bg=self.bg_color)
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.button_color, 
                             foreground=self.text_color, padding=[10, 5],
                             font=('Arial', 10, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', self.accent_color)],
                       foreground=[('selected', self.text_color)])

        # Ensure required directories exist
        os.makedirs("assets/logs", exist_ok=True)
        os.makedirs("assets/keys", exist_ok=True)
        os.makedirs("assets/files/encrypted", exist_ok=True)
        os.makedirs("assets/files/decrypted", exist_ok=True)
        os.makedirs("assets/database", exist_ok=True)
        
        # Initialize database
        database.ensure_db_exists()

        # Top frame with title and logout button
        self.top_frame = tk.Frame(self, bg=self.bg_color)
        self.top_frame.pack(fill="x")

        title_font = font.Font(family="Arial", size=18, weight="bold")
        self.title_label = tk.Label(self.top_frame, text="SecureFileVault", 
                                   font=title_font, bg=self.bg_color, fg=self.accent_color)
        self.title_label.pack(side="left", padx=15, pady=15)
        
        # Current user info (hidden initially)
        self.current_user_id = None
        self.current_user_label = tk.Label(self.top_frame, text="", bg=self.bg_color, fg=self.text_color)

        self.content_frame = tk.Frame(self, bg=self.bg_color)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Logout button (hidden initially)
        self.logout_button = tk.Button(
            self.top_frame, 
            text="🚪 Logout", 
            command=self.on_logout,
            bg="#e74c3c", 
            fg="white", 
            font=("Arial", 10, "bold"),
            padx=10, 
            pady=5, 
            border=0, 
            cursor="hand2",
            activebackground="#c0392b", 
            activeforeground="white"
        )
        self.logout_button.pack(side="right", padx=15, pady=15)
        self.logout_button.pack_forget()

        # Tab control for main interface
        self.tab_control = ttk.Notebook(self.content_frame)
        self.tab_control.pack(fill="both", expand=True)

        # Initialize login and register tabs
        self.login_tab = login_tab.LoginTab(
            self.tab_control, 
            self.on_login_success,
            self.on_register, 
            bg_color=self.bg_color, 
            accent_color=self.accent_color,
            text_color=self.text_color, 
            button_color=self.button_color
        )
        
        self.register_tab = register_tab.RegisterTab(
            self.tab_control, 
            self.on_register_success,
            bg_color=self.bg_color, 
            accent_color=self.accent_color,
            text_color=self.text_color, 
            button_color=self.button_color
        )
        
        # Other tabs are created on successful login
        self.vault_tab = None
        self.firewall_tab = None
        self.log_tab = None
        self.profile_tab = None
        self.admin_tab = None
        self.file_sharing_tab = None
        self.change_password_tab = None

        # Start with login tab
        self.tab_control.add(self.login_tab, text="Login")

        # Footer
        self.footer_frame = tk.Frame(self, bg=self.bg_color, height=30)
        self.footer_frame.pack(fill="x", side="bottom")
        tk.Label(
            self.footer_frame, 
            text="© 2025 SecureFileVault | Secured with Advanced Encryption", 
            bg=self.bg_color, 
            fg="#6c7983", 
            font=("Arial", 8)
        ).pack(pady=5)

    def on_login_success(self, user_id):
        """Switch to main tabs after successful login"""
        # Store the current user ID
        self.current_user_id = user_id
        
        # Get user profile for display
        user_profile = database.get_user_profile(user_id)
        
        # Update user label
        self.current_user_label.config(text=f"Logged in as: {user_profile['username']}")
        self.current_user_label.pack(side="left", padx=(10, 0))
        
        # Remove login and register tabs
        self.tab_control.forget(self.login_tab)
        if self.tab_control.index("end") > 0:  # Check if register tab is present
            self.tab_control.forget(self.register_tab)
        
        # Create and add Vault tab (always available)
        self.vault_tab = vault_tab.VaultTab(
            self.tab_control,
            bg_color=self.bg_color, 
            accent_color=self.accent_color,
            text_color=self.text_color, 
            button_color=self.button_color
        )
        self.tab_control.add(self.vault_tab, text="Vault")
        
        # Add Firewall tab based on permissions or admin status
        if user_profile['can_access_firewall'] or user_profile['account_type'] == 'admin':
            self.firewall_tab = firewall_tab.FirewallTab(
                self.tab_control,
                bg_color=self.bg_color, 
                accent_color=self.accent_color,
                text_color=self.text_color, 
                button_color=self.button_color
            )
            self.tab_control.add(self.firewall_tab, text="Firewall")
        
        # Add Logs tab based on permissions or admin status
        if user_profile['can_access_logs'] or user_profile['account_type'] == 'admin':
            self.log_tab = log_tab.LogTab(
                self.tab_control,
                bg_color=self.bg_color, 
                accent_color=self.accent_color,
                text_color=self.text_color, 
                button_color=self.button_color
            )
            self.tab_control.add(self.log_tab, text="Logs")
        
        # Add File Sharing tab (available to all users)
        self.file_sharing_tab = file_sharing_tab.FileSharingTab(
            self.tab_control,
            user_id,
            bg_color=self.bg_color, 
            accent_color=self.accent_color,
            text_color=self.text_color, 
            button_color=self.button_color
        )
        self.tab_control.add(self.file_sharing_tab, text="File Sharing")
        
        # Add Profile tab (available to all users)
        self.profile_tab = profile_tab.ProfileTab(
                self.tab_control,
                user_id,
                on_change_password=self.show_change_password_tab,  # Changed parameter name to match pattern
                bg_color=self.bg_color,
                accent_color=self.accent_color,
                text_color=self.text_color,
                button_color=self.button_color
            )
        self.tab_control.add(self.profile_tab, text="Profile")
        
        # Add Admin tab only for admin users
        if user_profile['account_type'] == 'admin':
            self.admin_tab = admin_tab.AdminTab(
                self.tab_control,
                user_id,
                bg_color=self.bg_color, 
                accent_color=self.accent_color,
                text_color=self.text_color, 
                button_color=self.button_color
            )
            self.tab_control.add(self.admin_tab, text="Admin")
        
        # Show logout button
        self.logout_button.pack(side="right", padx=15, pady=15)
        
        # Log the login
        database.log_user_activity(user_id, "Login", "User logged in successfully")

    def show_change_password_tab(self):
        """Show the change password tab"""
        if not self.change_password_tab:
            self.change_password_tab = change_password_tab.ChangePasswordTab(
                self.tab_control,
                self.current_user_id,
                on_success_callback=self.show_profile_tab,  # Consistent parameter naming
                bg_color=self.bg_color,
                accent_color=self.accent_color,
                text_color=self.text_color,
                button_color=self.button_color
            )
        self.tab_control.forget(self.profile_tab)
        self.tab_control.add(self.change_password_tab, text="Change Password")
            
    def show_profile_tab(self):
        """Return to profile tab"""
        self.tab_control.forget(self.change_password_tab)
        self.tab_control.add(self.profile_tab, text="Profile")
            
    def on_logout(self):
        """Return to login screen"""
        if self.current_user_id:
            database.log_user_activity(self.current_user_id, "Logout", "User logged out")
        
        # Destroy all existing tabs
        for tab in self.tab_control.tabs():
            self.tab_control.forget(tab)
        
        # Reset tab references
        self.vault_tab = None
        self.firewall_tab = None
        self.log_tab = None
        self.profile_tab = None
        self.admin_tab = None
        self.file_sharing_tab = None
        self.change_password_tab = None
        
        # Recreate login tab
        self.login_tab = login_tab.LoginTab(
            self.tab_control, 
            self.on_login_success,
            self.on_register,
            bg_color=self.bg_color, 
            accent_color=self.accent_color,
            text_color=self.text_color, 
            button_color=self.button_color
        )
        self.tab_control.add(self.login_tab, text="Login")
        
        # Reset user info
        self.current_user_id = None
        self.current_user_label.config(text="")
        self.current_user_label.pack_forget()
        self.logout_button.pack_forget()
        
        # Clear any existing entries in login form
        if hasattr(self.login_tab, 'username_entry'):
            self.login_tab.username_entry.delete(0, tk.END)
        if hasattr(self.login_tab, 'password_entry'):
            self.login_tab.password_entry.delete(0, tk.END)
        if hasattr(self.login_tab, 'otp_entry'):
            self.login_tab.otp_entry.delete(0, tk.END)
        if hasattr(self.login_tab, 'status_label'):
            self.login_tab.status_label.config(text="")
    
    def on_register(self):
        """Switch to registration tab"""
        self.tab_control.forget(self.login_tab)
        self.tab_control.add(self.register_tab, text="Create Account")
    
    def on_register_success(self):
        """Return to login after successful registration"""
        self.tab_control.forget(self.register_tab)
        self.tab_control.add(self.login_tab, text="Login")

if __name__ == "__main__":
    app = SecureFileVaultApp()
    app.mainloop()
