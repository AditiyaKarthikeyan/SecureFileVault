
import tkinter as tk
from tkinter import messagebox, font
import pyotp
import qrcode
from PIL import Image, ImageTk
import io
import re
from core import database, logger

class RegisterTab(tk.Frame):
    def __init__(self, master, on_success_callback, bg_color="#0c1e2f", 
                 accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.on_success = on_success_callback
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        # Generate a new TOTP secret for registration
        self.secret = pyotp.random_base32()
        self.totp = pyotp.TOTP(self.secret)
        
        # Create a container frame with scrollbar
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        
        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Create a container frame for content
        self.container = tk.Frame(self.scrollable_frame, bg=bg_color, padx=20, pady=20)
        self.container.pack(fill="x", expand=True)
        
        # Title with gradient-like effect
        title_frame = tk.Frame(self.container, bg=bg_color)
        title_frame.pack(pady=10)
        
        header_font = font.Font(family="Arial", size=24, weight="bold")
        tk.Label(title_frame, text="Create Account", font=header_font, 
                 bg=bg_color, fg=accent_color).pack()
        
        sub_font = font.Font(family="Arial", size=12)
        tk.Label(title_frame, text="Join SecureFileVault with enhanced security", font=sub_font,
                 bg=bg_color, fg=text_color).pack(pady=(5,10))
        
        # Registration form
        form_frame = tk.Frame(self.container, bg=bg_color, padx=20, pady=10)
        form_frame.pack(fill="x")
        
        # Username field
        tk.Label(form_frame, text="Username:", bg=bg_color, fg=text_color, font=("Arial", 12),
                 anchor="w").pack(fill="x", pady=(10, 5))
        self.username_entry = tk.Entry(form_frame, font=("Arial", 11), bg="#214c78", fg=text_color,
                                       insertbackground=text_color, relief=tk.FLAT, bd=0)
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 10))
        
        # Password field
        tk.Label(form_frame, text="Password:", bg=bg_color, fg=text_color, font=("Arial", 12),
                 anchor="w").pack(fill="x", pady=(10, 5))
        self.password_entry = tk.Entry(form_frame, show="•", font=("Arial", 11), bg="#214c78", 
                                       fg=text_color, insertbackground=text_color, relief=tk.FLAT, bd=0)
        self.password_entry.pack(fill="x", ipady=8, pady=(0, 10))
        
        # Confirm Password field
        tk.Label(form_frame, text="Confirm Password:", bg=bg_color, fg=text_color, font=("Arial", 12),
                 anchor="w").pack(fill="x", pady=(10, 5))
        self.confirm_password_entry = tk.Entry(form_frame, show="•", font=("Arial", 11), bg="#214c78", 
                                              fg=text_color, insertbackground=text_color, relief=tk.FLAT, bd=0)
        self.confirm_password_entry.pack(fill="x", ipady=8, pady=(0, 10))
        
        # Full Name field
        tk.Label(form_frame, text="Full Name:", bg=bg_color, fg=text_color, font=("Arial", 12),
                 anchor="w").pack(fill="x", pady=(10, 5))
        self.fullname_entry = tk.Entry(form_frame, font=("Arial", 11), bg="#214c78", fg=text_color,
                                       insertbackground=text_color, relief=tk.FLAT, bd=0)
        self.fullname_entry.pack(fill="x", ipady=8, pady=(0, 10))
        
        # Email field
        tk.Label(form_frame, text="Email:", bg=bg_color, fg=text_color, font=("Arial", 12),
                 anchor="w").pack(fill="x", pady=(10, 5))
        self.email_entry = tk.Entry(form_frame, font=("Arial", 11), bg="#214c78", fg=text_color,
                                    insertbackground=text_color, relief=tk.FLAT, bd=0)
        self.email_entry.pack(fill="x", ipady=8, pady=(0, 10))
        
        # 2FA Setup
        tk.Label(form_frame, text="Two-Factor Authentication Setup:", bg=bg_color, fg=text_color, 
                 font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=(20, 10))
        
        # Instructions
        instructions = (
            "1. Download Google Authenticator or similar TOTP app\n"
            "2. Scan the QR code below with the app\n"
            "3. Enter the code shown in your app"
        )
        tk.Label(form_frame, text=instructions, bg=bg_color, fg=text_color, 
                 font=("Arial", 10), anchor="w", justify=tk.LEFT).pack(fill="x", pady=(0, 10))
        
        # Generate and display QR code
        qr_frame = tk.Frame(form_frame, bg=bg_color)
        qr_frame.pack(pady=10)
        
        totp_uri = self.totp.provisioning_uri(name="SecureFileVault", issuer_name="SecureFileVault")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL image to Tkinter compatible image
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        qr_image = ImageTk.PhotoImage(Image.open(buffer))
        
        qr_label = tk.Label(qr_frame, image=qr_image, bg=bg_color)
        qr_label.image = qr_image  # Keep a reference to prevent garbage collection
        qr_label.pack()
        
        # Verification code
        tk.Label(form_frame, text="Verification Code:", bg=bg_color, fg=text_color, font=("Arial", 12),
                 anchor="w").pack(fill="x", pady=(10, 5))
        self.otp_entry = tk.Entry(form_frame, font=("Arial", 11), bg="#214c78", fg=text_color,
                                 insertbackground=text_color, relief=tk.FLAT, bd=0)
        self.otp_entry.pack(fill="x", ipady=8, pady=(0, 10))
        
        
        # Button frame for Register and Back buttons
        button_frame = tk.Frame(form_frame, bg=bg_color)
        button_frame.pack(fill="x", pady=15)
        
        # Register button
        self.register_button = tk.Button(button_frame, text="Create Account", command=self.register,
                                    bg=accent_color, fg="#ffffff", font=("Arial", 12, "bold"),
                                    padx=20, pady=8, relief=tk.FLAT, bd=0, cursor="hand2",
                                    activebackground="#319795", activeforeground="#ffffff")
        self.register_button.pack(side=tk.LEFT, fill="x", expand=True, padx=(0, 5))
        
        # Back to Login button
        self.back_button = tk.Button(button_frame, text="Back to Login", command=self.on_success,
                                bg=button_color, fg="#ffffff", font=("Arial", 12, "bold"),
                                padx=20, pady=8, relief=tk.FLAT, bd=0, cursor="hand2",
                                activebackground="#102a43", activeforeground="#ffffff")
        self.back_button.pack(side=tk.RIGHT, fill="x", expand=True, padx=(5, 0))
        
        # Login link removed as we now have a proper button
        
        # Status message
        self.status_label = tk.Label(form_frame, text="", fg="#e74c3c", bg=bg_color)
        self.status_label.pack(pady=10)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def validate_email(self, email):
        """Simple email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def register(self):
        """Register a new user"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        full_name = self.fullname_entry.get()
        email = self.email_entry.get()
        otp = self.otp_entry.get()
        
        # Validation
        if not all([username, password, confirm_password, full_name, email, otp]):
            self.status_label.config(text="All fields are required.")
            return
        
        if password != confirm_password:
            self.status_label.config(text="Passwords do not match.")
            return
            
        if len(password) < 8:
            self.status_label.config(text="Password must be at least 8 characters.")
            return
            
        if not self.validate_email(email):
            self.status_label.config(text="Please enter a valid email address.")
            return
            
        # Verify OTP
        if not self.totp.verify(otp, valid_window=1):
            self.status_label.config(text="Invalid verification code.")
            return
            
        # Register user in database
        success = database.register_user(username, password, full_name, email, self.secret)
        
        if success:
            logger.log_event(f"User registered: {username}")
            messagebox.showinfo("Success", "Account created successfully! You can now log in.")
            self.on_success()  # Return to login screen
        else:
            self.status_label.config(text="Username already exists. Please choose another.")

