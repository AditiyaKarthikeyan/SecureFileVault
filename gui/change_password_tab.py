import tkinter as tk
from tkinter import font, messagebox
from core import database

class ChangePasswordTab(tk.Frame):
    def __init__(self, master, user_id, on_success_callback, bg_color="#0c1e2f", 
                 accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.user_id = user_id
        self.on_success = on_success_callback
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        # Password requirements information
        self.password_requirements = (
            "• At least 8 characters\n"
            "• At least one uppercase letter\n"
            "• At least one number\n"
            "• At least one special character"
        )
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the password change UI"""
        # Main container
        container = tk.Frame(self, bg=self.bg_color, padx=25, pady=25)
        container.pack(expand=True, fill="both")
        
        # Title section
        title_frame = tk.Frame(container, bg=self.bg_color)
        title_frame.pack(pady=(0, 15))
        
        header_font = font.Font(family="Arial", size=24, weight="bold")
        tk.Label(title_frame, 
                text="Change Password", 
                font=header_font, 
                bg=self.bg_color, 
                fg=self.accent_color).pack()
        
        sub_font = font.Font(family="Arial", size=12)
        tk.Label(title_frame, 
                text="Enter your current password and set a new one", 
                font=sub_font,
                bg=self.bg_color, 
                fg=self.text_color).pack(pady=(5, 20))
        
        # Form section
        form_frame = tk.Frame(container, bg=self.bg_color, padx=20, pady=10)
        form_frame.pack(fill="x")
        
        # Current Password field
        tk.Label(form_frame, 
                text="Current Password:", 
                bg=self.bg_color, 
                fg=self.text_color, 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.current_pass = tk.Entry(form_frame, 
                                   show="•", 
                                   font=("Arial", 11), 
                                   bg="#214c78", 
                                   fg=self.text_color, 
                                   relief=tk.FLAT,
                                   insertbackground=self.text_color)
        self.current_pass.pack(fill="x", ipady=8, pady=(0, 15))
        
        # New Password field
        tk.Label(form_frame, 
                text="New Password:", 
                bg=self.bg_color, 
                fg=self.text_color, 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.new_pass = tk.Entry(form_frame, 
                               show="•", 
                               font=("Arial", 11), 
                               bg="#214c78", 
                               fg=self.text_color, 
                               relief=tk.FLAT,
                               insertbackground=self.text_color)
        self.new_pass.pack(fill="x", ipady=8, pady=(0, 5))
        
        # Password requirements
        requirements_label = tk.Label(form_frame,
                                    text=self.password_requirements,
                                    bg=self.bg_color,
                                    fg="#6c7983",
                                    font=("Arial", 9),
                                    justify=tk.LEFT)
        requirements_label.pack(anchor="w", pady=(0, 15))
        
        # Confirm Password field
        tk.Label(form_frame, 
                text="Confirm New Password:", 
                bg=self.bg_color, 
                fg=self.text_color, 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=(10, 5))
        
        self.confirm_pass = tk.Entry(form_frame, 
                                   show="•", 
                                   font=("Arial", 11), 
                                   bg="#214c78", 
                                   fg=self.text_color, 
                                   relief=tk.FLAT,
                                   insertbackground=self.text_color)
        self.confirm_pass.pack(fill="x", ipady=8, pady=(0, 15))
        
        # Button section
        button_frame = tk.Frame(form_frame, bg=self.bg_color)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Change Password button
        self.change_btn = tk.Button(
            button_frame,
            text="Change Password",
            command=self.change_password,
            bg=self.accent_color,
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            activebackground="#319795",
            cursor="hand2"
        )
        self.change_btn.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Back button
        self.back_btn = tk.Button(
            button_frame,
            text="Back to Profile",
            command=self.on_success,
            bg=self.button_color,
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.FLAT,
            activebackground="#102a43",
            cursor="hand2"
        )
        self.back_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Status label
        self.status_label = tk.Label(form_frame, 
                                    text="", 
                                    fg="#e74c3c", 
                                    bg=self.bg_color,
                                    font=("Arial", 11))
        self.status_label.pack(pady=(5, 0))

    def change_password(self):
        """Handle password change logic with comprehensive feedback"""
        current = self.current_pass.get().strip()
        new = self.new_pass.get().strip()
        confirm = self.confirm_pass.get().strip()
        
        # Clear previous status
        self.status_label.config(text="", fg="#e74c3c")
        
        # Validate fields
        if not all([current, new, confirm]):
            self.status_label.config(text="All fields are required.", fg="#e74c3c")
            return
            
        if new != confirm:
            self.status_label.config(text="New passwords do not match.", fg="#e74c3c")
            return
            
        if len(new) < 8:
            self.status_label.config(text="Password must be at least 8 characters.", fg="#e74c3c")
            return
            
        if not any(c.isupper() for c in new):
            self.status_label.config(text="Password needs at least one uppercase letter.", fg="#e74c3c")
            return
            
        if not any(c.isdigit() for c in new):
            self.status_label.config(text="Password needs at least one number.", fg="#e74c3c")
            return
            
        if not any(not c.isalnum() for c in new):
            self.status_label.config(text="Password needs at least one special character.", fg="#e74c3c")
            return
            
        # Verify current password
        if not database.verify_password(self.user_id, current):
            self.status_label.config(text="Current password is incorrect.", fg="#e74c3c")
            return
            
        # Disable buttons during processing
        self.change_btn.config(state=tk.DISABLED, text="Updating...")
        self.back_btn.config(state=tk.DISABLED)
        self.update()  # Force UI update
        
        try:
            # Attempt password update
            success, message = database.update_password(self.user_id, current, new)
            
            if success:
                # Clear fields on success
                self.current_pass.delete(0, tk.END)
                self.new_pass.delete(0, tk.END)
                self.confirm_pass.delete(0, tk.END)
                
                # Show success message
                self.status_label.config(
                    text="✓ Password updated successfully!", 
                    fg="#2ecc71",
                    font=("Arial", 11, "bold")
                )
                
                # Log the successful change
                database.log_user_activity(
                    self.user_id, 
                    "Password Change", 
                    "User changed their password successfully"
                )
                
                # Auto-return to profile after 2 seconds
                self.after(2000, self.on_success)
            else:
                # Show error message from database
                self.status_label.config(
                    text=f"Error: {message}", 
                    fg="#e74c3c"
                )
                
                # Log the failed attempt
                database.log_user_activity(
                    self.user_id, 
                    "Password Change Failed", 
                    f"Failed to change password: {message}"
                )
                
        except Exception as e:
            # Handle unexpected errors
            self.status_label.config(
                text="System error occurred. Please try again.", 
                fg="#e74c3c"
            )
            
            # Log the error
            database.log_user_activity(
                self.user_id, 
                "Password Change Error", 
                f"System error during password change: {str(e)}"
            )
            
        finally:
            # Restore button states
            self.change_btn.config(state=tk.NORMAL, text="Change Password")
            self.back_btn.config(state=tk.NORMAL)
