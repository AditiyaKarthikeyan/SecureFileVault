
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from core import database, crypto_module, logger

class FileSharingTab(tk.Frame):
    def __init__(self, master, user_id, bg_color="#0c1e2f", 
                 accent_color="#38b2ac", text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.user_id = user_id
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        
        # Get the current user information
        self.user_profile = database.get_user_profile(user_id)
        
        # Create a notebook for inbox/outbox
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Style for the notebook
        style = ttk.Style()
        style.configure('Custom.TNotebook.Tab', padding=[12, 8], font=('Arial', 10, 'bold'))
        
        # Create inbox tab
        self.inbox_frame = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.inbox_frame, text="Inbox")
        
        # Create outbox tab
        self.outbox_frame = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.outbox_frame, text="Outbox")
        
        # Create compose tab
        self.compose_frame = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.compose_frame, text="Send File")
        
        # Setup each tab
        self._setup_inbox()
        self._setup_outbox()
        self._setup_compose()
        
        # Refresh messages on tab change
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)
        
    def _setup_inbox(self):
        """Setup the inbox tab to display received files"""
        # Title
        inbox_title = tk.Label(
            self.inbox_frame, 
            text="Secure File Inbox", 
            font=("Arial", 16, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        inbox_title.pack(pady=(20, 10))
        
        # Description
        description = tk.Label(
            self.inbox_frame, 
            text="Files shared with you by other users appear here.", 
            font=("Arial", 10), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        description.pack(pady=(0, 20))
        
        # Create a frame for the message list
        list_frame = tk.Frame(self.inbox_frame, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create scrollable frame for messages
        self.inbox_canvas = tk.Canvas(list_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.inbox_canvas.yview)
        
        self.inbox_scrollable_frame = tk.Frame(self.inbox_canvas, bg=self.bg_color)
        self.inbox_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.inbox_canvas.configure(scrollregion=self.inbox_canvas.bbox("all"))
        )
        
        self.inbox_canvas.create_window((0, 0), window=self.inbox_scrollable_frame, anchor="nw")
        self.inbox_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.inbox_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_button = tk.Button(
            self.inbox_frame,
            text="Refresh",
            command=self._load_inbox,
            bg=self.button_color,
            fg=self.text_color,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        refresh_button.pack(pady=10)
        
        # Load inbox messages
        self._load_inbox()
    
    def _setup_outbox(self):
        """Setup the outbox tab to display sent files"""
        # Title
        outbox_title = tk.Label(
            self.outbox_frame, 
            text="Sent Files", 
            font=("Arial", 16, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        outbox_title.pack(pady=(20, 10))
        
        # Description
        description = tk.Label(
            self.outbox_frame, 
            text="Files you've shared with other users appear here.", 
            font=("Arial", 10), 
            bg=self.bg_color, 
            fg=self.text_color
        )
        description.pack(pady=(0, 20))
        
        # Create a frame for the message list
        list_frame = tk.Frame(self.outbox_frame, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create scrollable frame for messages
        self.outbox_canvas = tk.Canvas(list_frame, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.outbox_canvas.yview)
        
        self.outbox_scrollable_frame = tk.Frame(self.outbox_canvas, bg=self.bg_color)
        self.outbox_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.outbox_canvas.configure(scrollregion=self.outbox_canvas.bbox("all"))
        )
        
        self.outbox_canvas.create_window((0, 0), window=self.outbox_scrollable_frame, anchor="nw")
        self.outbox_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.outbox_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Refresh button
        refresh_button = tk.Button(
            self.outbox_frame,
            text="Refresh",
            command=self._load_outbox,
            bg=self.button_color,
            fg=self.text_color,
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        refresh_button.pack(pady=10)
        
        # Load outbox messages
        self._load_outbox()
    
    def _setup_compose(self):
        """Setup the compose tab to send files"""
        # Title
        compose_title = tk.Label(
            self.compose_frame, 
            text="Send Secure File", 
            font=("Arial", 16, "bold"), 
            bg=self.bg_color, 
            fg=self.accent_color
        )
        compose_title.pack(pady=(20, 10))
        
        # Container for the form
        form_frame = tk.Frame(self.compose_frame, bg=self.bg_color)
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Recipient selection
        tk.Label(
            form_frame,
            text="Recipient:",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color,
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        # Get all users for recipient dropdown
        users = database.get_all_users()
        recipient_options = [f"{user['username']} ({user['full_name']})" for user in users if user['id'] != self.user_id]
        
        self.recipient_var = tk.StringVar()
        if recipient_options:
            self.recipient_var.set(recipient_options[0])
        
        recipient_dropdown = ttk.Combobox(
            form_frame,
            textvariable=self.recipient_var,
            values=recipient_options,
            state="readonly",
            font=("Arial", 11)
        )
        recipient_dropdown.pack(fill="x", ipady=8, pady=(0, 15))
        
        # File selection
        tk.Label(
            form_frame,
            text="Select File:",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color,
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        file_frame = tk.Frame(form_frame, bg=self.bg_color)
        file_frame.pack(fill="x", pady=(0, 15))
        
        self.file_path_var = tk.StringVar()
        self.file_path_var.set("No file selected")
        
        file_path_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path_var,
            font=("Arial", 11),
            bg="#214c78",
            fg=self.text_color,
            relief=tk.FLAT,
            state="readonly"
        )
        file_path_entry.pack(side="left", fill="x", expand=True, ipady=8)
        
        browse_button = tk.Button(
            file_frame,
            text="Browse",
            command=self._browse_file,
            bg=self.button_color,
            fg=self.text_color,
            font=("Arial", 10),
            padx=10
        )
        browse_button.pack(side="right", padx=(10, 0))
        
        # Message
        tk.Label(
            form_frame,
            text="Message (Optional):",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.text_color,
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        self.message_text = tk.Text(
            form_frame,
            height=5,
            font=("Arial", 11),
            bg="#214c78",
            fg=self.text_color,
            relief=tk.FLAT,
            wrap=tk.WORD
        )
        self.message_text.pack(fill="x", ipady=5, pady=(0, 15))
        
        # Send button
        send_button = tk.Button(
            form_frame,
            text="Send Secure File",
            command=self._send_file,
            bg=self.accent_color,
            fg="#ffffff",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8,
            relief=tk.FLAT
        )
        send_button.pack(pady=20)
        
        # Status message
        self.status_label = tk.Label(
            form_frame,
            text="",
            bg=self.bg_color,
            fg="#e74c3c",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
    
    def _browse_file(self):
        """Open file dialog to select a file"""
        file_path = filedialog.askopenfilename(
            title="Select File to Share",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def _send_file(self):
        """Send encrypted file to the selected recipient"""
        # Clear previous status
        self.status_label.config(text="")
        
        # Get recipient
        recipient_selection = self.recipient_var.get()
        if not recipient_selection:
            self.status_label.config(text="Please select a recipient")
            return
        
        # Extract username from selection
        recipient_username = recipient_selection.split(" ")[0]
        
        # Find recipient ID
        users = database.get_all_users()
        recipient_id = next((user['id'] for user in users if user['username'] == recipient_username), None)
        
        if not recipient_id:
            self.status_label.config(text="Invalid recipient")
            return
        
        # Get file path
        file_path = self.file_path_var.get()
        if file_path == "No file selected":
            self.status_label.config(text="Please select a file to send")
            return
        
        # Get message
        message = self.message_text.get("1.0", tk.END).strip()
        
        try:
            # Encrypt the file
            self.status_label.config(text="Encrypting file...")
            encrypted_path = crypto_module.encrypt_file(file_path)
            
            # Save the message with file reference
            database.save_secure_message(
                self.user_id, 
                recipient_id, 
                message, 
                encrypted_path
            )
            
            # Log the activity
            filename = os.path.basename(file_path)
            database.log_user_activity(
                self.user_id, 
                "File Shared", 
                f"Shared encrypted file '{filename}' with {recipient_username}"
            )
            logger.log_event(f"User {self.user_profile['username']} shared file with {recipient_username}")
            
            # Clear form
            self.file_path_var.set("No file selected")
            self.message_text.delete("1.0", tk.END)
            
            # Show success
            self.status_label.config(text="File sent securely!", fg="#2ecc71")
            
            # Refresh outbox
            self._load_outbox()
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            logger.log_event(f"Error sharing file: {str(e)}")
    
    def _load_inbox(self):
        """Load inbox messages"""
        # Clear existing messages
        for widget in self.inbox_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get messages
        messages = database.get_user_messages(self.user_id, "incoming")
        
        if not messages:
            empty_label = tk.Label(
                self.inbox_scrollable_frame,
                text="Your inbox is empty",
                font=("Arial", 12),
                bg=self.bg_color,
                fg=self.text_color
            )
            empty_label.pack(pady=20)
            return
        
        # Display messages
        for msg in messages:
            msg_frame = tk.Frame(self.inbox_scrollable_frame, bg=self.button_color, padx=15, pady=15)
            msg_frame.pack(fill="x", pady=5, padx=10)
            
            # Header with sender and date
            header_frame = tk.Frame(msg_frame, bg=self.button_color)
            header_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(
                header_frame,
                text=f"From: {msg['sender_name']}",
                font=("Arial", 11, "bold"),
                bg=self.button_color,
                fg=self.accent_color,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                header_frame,
                text=msg['sent_at'],
                font=("Arial", 9),
                bg=self.button_color,
                fg="#6c7983",
                anchor="e"
            ).pack(side="right")
            
            # Message body if exists
            if msg['message']:
                tk.Label(
                    msg_frame,
                    text=msg['message'],
                    font=("Arial", 10),
                    bg=self.button_color,
                    fg=self.text_color,
                    justify="left",
                    wraplength=500
                ).pack(fill="x", anchor="w", pady=(0, 10))
            
            # File attachment
            if msg['file_path']:
                file_frame = tk.Frame(msg_frame, bg=self.button_color)
                file_frame.pack(fill="x", pady=5)
                
                filename = os.path.basename(msg['file_path']).replace("encrypted_", "")
                tk.Label(
                    file_frame,
                    text=f"📎 {filename}",
                    font=("Arial", 10),
                    bg=self.button_color,
                    fg=self.text_color,
                    anchor="w"
                ).pack(side="left")
                
                download_button = tk.Button(
                    file_frame,
                    text="Decrypt & Download",
                    command=lambda path=msg['file_path']: self._decrypt_file(path),
                    bg=self.accent_color,
                    fg="#ffffff",
                    font=("Arial", 9, "bold"),
                    padx=10,
                    pady=3
                )
                download_button.pack(side="right")
            
            # Mark as read if not already
            if not msg['read_at'] and msg['file_path']:
                database.mark_message_as_read(msg['id'])
    
    def _load_outbox(self):
        """Load outbox messages"""
        # Clear existing messages
        for widget in self.outbox_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get messages
        messages = database.get_user_messages(self.user_id, "outgoing")
        
        if not messages:
            empty_label = tk.Label(
                self.outbox_scrollable_frame,
                text="You haven't sent any files yet",
                font=("Arial", 12),
                bg=self.bg_color,
                fg=self.text_color
            )
            empty_label.pack(pady=20)
            return
        
        # Display messages
        for msg in messages:
            msg_frame = tk.Frame(self.outbox_scrollable_frame, bg=self.button_color, padx=15, pady=15)
            msg_frame.pack(fill="x", pady=5, padx=10)
            
            # Header with recipient and date
            header_frame = tk.Frame(msg_frame, bg=self.button_color)
            header_frame.pack(fill="x", pady=(0, 10))
            
            tk.Label(
                header_frame,
                text=f"To: {msg['recipient_name']}",
                font=("Arial", 11, "bold"),
                bg=self.button_color,
                fg=self.accent_color,
                anchor="w"
            ).pack(side="left")
            
            tk.Label(
                header_frame,
                text=msg['sent_at'],
                font=("Arial", 9),
                bg=self.button_color,
                fg="#6c7983",
                anchor="e"
            ).pack(side="right")
            
            # Message body if exists
            if msg['message']:
                tk.Label(
                    msg_frame,
                    text=msg['message'],
                    font=("Arial", 10),
                    bg=self.button_color,
                    fg=self.text_color,
                    justify="left",
                    wraplength=500
                ).pack(fill="x", anchor="w", pady=(0, 10))
            
            # File attachment info
            if msg['file_path']:
                filename = os.path.basename(msg['file_path']).replace("encrypted_", "")
                tk.Label(
                    msg_frame,
                    text=f"📎 {filename}",
                    font=("Arial", 10),
                    bg=self.button_color,
                    fg=self.text_color,
                    anchor="w"
                ).pack(fill="x")
                
                # Read status
                status_text = "Read" if msg['read_at'] else "Not read yet"
                status_color = "#2ecc71" if msg['read_at'] else "#e74c3c"
                tk.Label(
                    msg_frame,
                    text=status_text,
                    font=("Arial", 9),
                    bg=self.button_color,
                    fg=status_color,
                    anchor="e"
                ).pack(anchor="e")
    
    def _decrypt_file(self, file_path):
        """Decrypt a received file"""
        try:
            decrypted_path = crypto_module.decrypt_file(file_path)
            
            # Success message
            messagebox.showinfo(
                "File Decrypted", 
                f"File has been decrypted and saved to:\n{decrypted_path}"
            )
            
            database.log_user_activity(
                self.user_id, 
                "File Decrypted", 
                f"Decrypted file: {os.path.basename(decrypted_path)}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt file: {str(e)}")
    
    def _on_tab_change(self, event):
        """Handle tab change event"""
        tab_id = self.notebook.index("current")
        
        # Refresh appropriate tab
        if tab_id == 0:  # Inbox
            self._load_inbox()
        elif tab_id == 1:  # Outbox
            self._load_outbox()
