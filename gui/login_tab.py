
import tkinter as tk
from tkinter import messagebox, font
import pyotp
from core import logger, database

class LoginTab(tk.Frame):
    def __init__(self, master, on_success_callback, on_register_callback=None, bg_color="#0c1e2f", 
                 accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.on_success = on_success_callback
        self.on_register = on_register_callback
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        self.current_user_id = None

        # TOTP setup (fixed for demo/testing)
        self.secret = "HX3YB5DQOIZV2ZLZ"
        self.totp = pyotp.TOTP(self.secret)

        # Container
        self.container = tk.Frame(self, bg=bg_color, padx=20, pady=20)
        self.container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        title_frame = tk.Frame(self.container, bg=bg_color)
        title_frame.pack(pady=20)

        # Font handling with fallback
        try:
            header_font = font.Font(family="Arial", size=24, weight="bold")
            sub_font = font.Font(family="Arial", size=12)
        except:
            header_font = font.nametofont("TkDefaultFont")
            header_font.configure(size=24, weight="bold")
            sub_font = font.nametofont("TkDefaultFont")
            sub_font.configure(size=12)

        # Title labels
        tk.Label(
            title_frame, 
            text="SecureFileVault", 
            font=header_font, 
            bg=bg_color, 
            fg=accent_color
        ).pack()
        
        tk.Label(
            title_frame, 
            text="Advanced Security Login", 
            font=sub_font,
            bg=bg_color, 
            fg=text_color
        ).pack(pady=(5, 20))

        # Form frame
        form_frame = tk.Frame(self.container, bg=bg_color, padx=20, pady=10)
        form_frame.pack(fill="x")

        # Common entry style
        entry_style = {
            "font": ("Arial", 11),
            "bg": "#214c78",
            "fg": text_color,
            "insertbackground": text_color,
            "relief": tk.FLAT,
            "bd": 0
        }

        # Username field
        tk.Label(
            form_frame, 
            text="Username:", 
            bg=bg_color, 
            fg=text_color, 
            font=("Arial", 12),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.username_entry = tk.Entry(
            form_frame, 
            **entry_style
        )
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 10))

        # Password field
        tk.Label(
            form_frame, 
            text="Password:", 
            bg=bg_color, 
            fg=text_color, 
            font=("Arial", 12),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.password_entry = tk.Entry(
            form_frame, 
            show="•", 
            **entry_style
        )
        self.password_entry.pack(fill="x", ipady=8, pady=(0, 10))

        # OTP field
        tk.Label(
            form_frame, 
            text="2FA Code:", 
            bg=bg_color, 
            fg=text_color, 
            font=("Arial", 12),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.otp_entry = tk.Entry(
            form_frame, 
            **entry_style
        )
        self.otp_entry.pack(fill="x", ipady=8, pady=(0, 15))  # Increased bottom padding

        # Testing note
        tk.Label(
            form_frame, 
            text="For testing: Use admin/admin123 and generate OTP", 
            bg=bg_color, 
            fg="#6c7983", 
            font=("Arial", 9)
        ).pack(pady=5)

        # Login button
        self.login_button = tk.Button(
            form_frame, 
            text="Login", 
            command=self.authenticate,
            bg=accent_color, 
            fg="#ffffff", 
            font=("Arial", 12, "bold"),
            padx=20, 
            pady=8, 
            relief=tk.FLAT, 
            bd=0, 
            cursor="hand2",
            activebackground="#319795", 
            activeforeground="#ffffff"
        )
        self.login_button.pack(fill="x")

        # Register link (if callback provided)
        if self.on_register:
            register_frame = tk.Frame(form_frame, bg=bg_color)
            register_frame.pack(pady=10)
            
            tk.Label(
                register_frame, 
                text="Don't have an account?", 
                bg=bg_color, 
                fg=text_color, 
                font=("Arial", 10)
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            register_link = tk.Label(
                register_frame, 
                text="Create one", 
                bg=bg_color, 
                fg=accent_color, 
                font=("Arial", 10, "underline"), 
                cursor="hand2"
            )
            register_link.pack(side=tk.LEFT)
            register_link.bind("<Button-1>", lambda e: self.on_register())

        # Status label
        self.status_label = tk.Label(
            form_frame, 
            text="", 
            fg="#e74c3c", 
            bg=bg_color,
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(10, 0))

    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        otp = self.otp_entry.get().strip()

        # Clear any previous error messages
        self.status_label.config(text="")
        
        if not all([username, password, otp]):
            self.status_label.config(text="All fields are required.")
            return
    
        # First authenticate with database
        user_id, totp_secret = database.authenticate_user(username, password)
        
        if not user_id:
            self.status_label.config(text="Invalid username or password.")
            logger.log_event(f"Failed login attempt: Invalid credentials for user: {username}")
            return
        
        # Then verify OTP
        totp = pyotp.TOTP(totp_secret)
        if totp.verify(otp, valid_window=1):  # Accepts current + previous/next OTP
            self.current_user_id = user_id
            database.log_user_activity(user_id, "Login", "User logged in successfully")
            logger.log_event(f"Successful login for user: {username}")
            self.on_success(user_id)
        else:
            self.status_label.config(text="Invalid or expired OTP code")
            logger.log_event(f"Failed login attempt: Invalid OTP for user: {username}")
