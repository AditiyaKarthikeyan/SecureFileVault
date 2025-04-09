import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk
import subprocess
import os
from core import crypto_module
from core import logger 

class VaultTab(tk.Frame):
    def __init__(self, master, bg_color="#0c1e2f", accent_color="#38b2ac", 
                 text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        self.create_ui()
        self.refresh_file_list()
        
    def create_ui(self):
        # Main container with two panels
        self.main_container = tk.PanedWindow(self, orient=tk.HORIZONTAL, 
                                             bg=self.bg_color, sashwidth=4, 
                                             sashrelief=tk.RAISED)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Left panel - Actions
        self.left_panel = tk.Frame(self.main_container, bg=self.bg_color, padx=10, pady=10)
        
        # Header
        header_font = font.Font(family="Arial", size=16, weight="bold")
        tk.Label(self.left_panel, text="Encrypted File Vault", font=header_font, 
                 bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 20))
        
        # Action buttons with icons
        button_frame = tk.Frame(self.left_panel, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Button style
        button_style = {
            "font": ("Arial", 11),
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 10,
            "width": 20
        }
        
        self.encrypt_btn = tk.Button(button_frame, text="🔒 Encrypt File", 
                                    bg=self.button_color, fg=self.text_color,
                                    activebackground=self.accent_color, 
                                    command=self.encrypt_file, **button_style)
        self.encrypt_btn.pack(fill=tk.X, pady=5)
        
        self.decrypt_btn = tk.Button(button_frame, text="🔓 Decrypt File", 
                                    bg=self.button_color, fg=self.text_color,
                                    activebackground=self.accent_color, 
                                    command=self.decrypt_file, **button_style)
        self.decrypt_btn.pack(fill=tk.X, pady=5)
        
        self.view_btn = tk.Button(button_frame, text="📄 View File", 
                                 bg=self.button_color, fg=self.text_color,
                                 activebackground=self.accent_color, 
                                 command=self.view_file, **button_style)
        self.view_btn.pack(fill=tk.X, pady=5)
        
        self.refresh_btn = tk.Button(button_frame, text="🔄 Refresh Files", 
                                    bg=self.button_color, fg=self.text_color,
                                    activebackground=self.accent_color, 
                                    command=self.refresh_file_list, **button_style)
        self.refresh_btn.pack(fill=tk.X, pady=5)
        
        # Status area
        status_frame = tk.Frame(self.left_panel, bg=self.bg_color, pady=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(status_frame, text="Status:", bg=self.bg_color, 
                 fg=self.text_color, font=("Arial", 11), anchor="w").pack(fill=tk.X)
        
        self.status_label = tk.Label(status_frame, text="Ready", bg="#214c78", 
                                    fg=self.text_color, font=("Arial", 10),
                                    padx=10, pady=10, anchor="w")
        self.status_label.pack(fill=tk.X, pady=5)
        
        # Right panel - File list
        self.right_panel = tk.Frame(self.main_container, bg=self.bg_color)
        
        # Search box
        search_frame = tk.Frame(self.right_panel, bg=self.bg_color, pady=10)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="Search Files:", bg=self.bg_color, 
                 fg=self.text_color).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, bg="#214c78", fg=self.text_color, 
                                    insertbackground=self.text_color, relief=tk.FLAT)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_files)
        
        # File treeview
        self.file_tree = ttk.Treeview(self.right_panel, columns=("type", "date"), show="headings")
        self.file_tree.heading("type", text="Type")
        self.file_tree.heading("date", text="Modified Date")
        self.file_tree.column("type", width=100)
        self.file_tree.column("date", width=150)
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#214c78", 
                        foreground=self.text_color, 
                        rowheight=25,
                        fieldbackground="#214c78")
        style.map("Treeview", background=[("selected", self.accent_color)])
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add panels to PanedWindow
        self.main_container.add(self.left_panel, width=250)
        self.main_container.add(self.right_panel)
        
        # Bind double-click to view files
        self.file_tree.bind("<Double-1>", lambda e: self.view_file())

    def encrypt_file(self):
        filepath = filedialog.askopenfilename(title="Select File to Encrypt")
        if filepath:
            try:
                self.status_label.config(text="Encrypting file...", fg="#f39c12")
                self.update_idletasks()
                
                # Create output path
                filename = os.path.basename(filepath)
                output_path = os.path.join("assets/files/encrypted", f"{filename}.enc")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                result_path = crypto_module.encrypt_file(filepath, output_path)
                self.status_label.config(text=f"Encrypted: {os.path.basename(result_path)}", 
                                        fg="#2ecc71")
                logger.log_event(f"Encrypted file: {filepath}")
                self.refresh_file_list()
            except Exception as e:
                self.status_label.config(text=f"Error: {str(e)}", fg="#e74c3c")
                messagebox.showerror("Encryption Error", str(e))

    def decrypt_file(self):
        selected = self.file_tree.selection()
        if selected:
            item = self.file_tree.item(selected[0])
            if item["values"][0] == "Encrypted":
                filepath = os.path.join("assets/files/encrypted", item["text"])
            else:
                messagebox.showwarning("Invalid File", "Please select an encrypted file")
                return
        else:
            filepath = filedialog.askopenfilename(initialdir="assets/files/encrypted", 
                                                title="Select File to Decrypt")
        
        if filepath:
            try:
                self.status_label.config(text="Decrypting file...", fg="#f39c12")
                self.update_idletasks()
                
                # Create output path
                filename = os.path.basename(filepath)
                if filename.endswith(".enc"):
                    filename = filename[:-4]  # Remove .enc extension
                output_path = os.path.join("assets/files/decrypted", filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                result_path = crypto_module.decrypt_file(filepath, output_path)
                self.status_label.config(text=f"Decrypted: {os.path.basename(result_path)}", 
                                        fg="#3498db")
                logger.log_event(f"Decrypted file: {filepath}")
                self.refresh_file_list()
            except Exception as e:
                self.status_label.config(text=f"Error: {str(e)}", fg="#e74c3c")
                messagebox.showerror("Decryption Error", str(e))

    def view_file(self):
        selected = self.file_tree.selection()
        if selected:
            item = self.file_tree.item(selected[0])
            file_type = item["values"][0]
            
            if file_type == "Encrypted":
                filepath = os.path.join("assets/files/encrypted", item["text"])
            else:
                filepath = os.path.join("assets/files/decrypted", item["text"])
        else:
            filepath = filedialog.askopenfilename(initialdir="assets/files/")
        
        if filepath:
            try:
                self.status_label.config(text=f"Opening: {os.path.basename(filepath)}", 
                                        fg=self.text_color)
                subprocess.run(["xdg-open", filepath])
                logger.log_event(f"Viewed file: {filepath}")
            except Exception as e:
                self.status_label.config(text=f"Cannot open file: {str(e)}", fg="#e74c3c")
                messagebox.showerror("View Error", f"Could not open file:\n{e}")
                logger.log_event(f"Failed to view: {filepath}")

    def refresh_file_list(self):
        # Clear existing items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Add encrypted files
        encrypted_dir = "assets/files/encrypted"
        if os.path.exists(encrypted_dir):
            for filename in os.listdir(encrypted_dir):
                filepath = os.path.join(encrypted_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    date_str = tk.Label().tk.call('clock', 'format', int(file_time), '-format', '%Y-%m-%d %H:%M')
                    self.file_tree.insert("", tk.END, text=filename, values=("Encrypted", date_str))
        
        # Add decrypted files
        decrypted_dir = "assets/files/decrypted"
        if os.path.exists(decrypted_dir):
            for filename in os.listdir(decrypted_dir):
                filepath = os.path.join(decrypted_dir, filename)
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    date_str = tk.Label().tk.call('clock', 'format', int(file_time), '-format', '%Y-%m-%d %H:%M')
                    self.file_tree.insert("", tk.END, text=filename, values=("Decrypted", date_str))
    
    def filter_files(self, event=None):
        search_term = self.search_entry.get().lower()
        self.refresh_file_list()  # First reload all files
        
        if search_term:
            # Then filter the displayed items
            for item in self.file_tree.get_children():
                filename = self.file_tree.item(item)["text"].lower()
                if search_term not in filename:
                    self.file_tree.detach(item)  # Hide non-matching items
