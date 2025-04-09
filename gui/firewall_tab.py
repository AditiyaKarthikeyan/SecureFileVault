import tkinter as tk
from tkinter import messagebox, font, ttk
import subprocess
import platform
import threading
from core import logger

class FirewallTab(tk.Frame):
    def __init__(self, master, bg_color="#0c1e2f", accent_color="#38b2ac", 
                 text_color="#ffffff", button_color="#163959"):
        super().__init__(master, bg=bg_color)
        self.bg_color = bg_color
        self.accent_color = accent_color
        self.text_color = text_color
        self.button_color = button_color
        self.shutting_down = False
        
        try:
            if not self._verify_system_ready():
                self.create_error_ui("System incompatible")
                return
                
            self._safe_ui_init()
            self._test_command_execution()
            
        except Exception as e:
            self.create_error_ui(f"Initialization failed: {str(e)}")
            logger.log_event(f"FirewallTab init failed: {str(e)}")

    def _verify_system_ready(self):
        """Check for required Linux firewall tools"""
        try:
            if platform.system() != "Linux":
                logger.log_event("FirewallTab loaded on non-Linux system")
                return False
                
            # Check for ufw
            ufw_check = subprocess.run(["which", "ufw"], 
                                     capture_output=True, 
                                     text=True)
            if ufw_check.returncode != 0:
                self.create_error_ui("ufw not found. Install with:\nsudo apt install ufw")
                return False
                
            # Check for ss
            ss_check = subprocess.run(["which", "ss"],
                                    capture_output=True,
                                    text=True)
            if ss_check.returncode != 0:
                self.create_error_ui("ss not found. Install with:\nsudo apt install iproute2")
                return False
                
            return True
            
        except Exception as e:
            logger.log_event(f"System verification failed: {str(e)}")
            return False

    def create_error_ui(self, message):
        """Show error message in the tab"""
        for widget in self.winfo_children():
            widget.destroy()
            
        error_frame = tk.Frame(self, bg=self.bg_color)
        error_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        tk.Label(
            error_frame,
            text="⚠️ Firewall Unavailable",
            font=("Arial", 14, "bold"),
            fg="#e74c3c",
            bg=self.bg_color
        ).pack(pady=10)
        
        tk.Label(
            error_frame,
            text=message,
            font=("Arial", 11),
            fg=self.text_color,
            bg=self.bg_color,
            wraplength=300
        ).pack()

    def _safe_ui_init(self):
        """Initialize the firewall UI components"""
        try:
            self.main_container = tk.PanedWindow(
                self,
                bg=self.bg_color,
                orient=tk.HORIZONTAL,
                sashwidth=4,
                sashrelief=tk.RAISED
            )
            self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            self._create_left_panel()
            self._create_right_panel()
            
            # Initial status check
            self.run_command(["sudo", "ufw", "status"], self.display_status)
            
        except Exception as e:
            self.create_error_ui(f"UI initialization failed: {str(e)}")
            logger.log_event(f"Firewall UI init failed: {str(e)}")

    def _create_left_panel(self):
        """Create left control panel"""
        self.left_panel = tk.Frame(self.main_container, bg=self.bg_color, padx=10, pady=10)
        
        try:
            header_font = font.Font(family="Arial", size=16, weight="bold")
        except:
            header_font = font.nametofont("TkDefaultFont")
            header_font.configure(size=16, weight="bold")
            
        tk.Label(
            self.left_panel, 
            text="🛡️ Firewall Controls", 
            font=header_font,
            bg=self.bg_color, 
            fg=self.accent_color
        ).pack(pady=(0, 15))
        
        self._create_status_controls()
        self._create_port_controls()
        self._create_network_controls()
        
        self.main_container.add(self.left_panel, width=250)

    def _create_status_controls(self):
        """Create firewall status controls"""
        button_style = {
            "font": ("Arial", 11),
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 8
        }
        
        status_frame = tk.LabelFrame(
            self.left_panel, 
            text="Firewall Status",
            padx=10, 
            pady=10,
            bg=self.bg_color, 
            fg=self.accent_color, 
            font=("Arial", 11, "bold")
        )
        status_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(
            status_frame, 
            text="🔍 Check Status", 
            bg=self.button_color, 
            fg=self.text_color, 
            command=lambda: self.run_command(["sudo", "ufw", "status"], self.display_status),
            activebackground=self.accent_color, 
            **button_style
        ).pack(fill=tk.X, pady=3)
        
        action_frame = tk.Frame(status_frame, bg=self.bg_color)
        action_frame.pack(fill=tk.X, pady=3)
        
        tk.Button(
            action_frame, 
            text="✅ Enable", 
            bg="#27ae60", 
            fg=self.text_color,
            command=lambda: self.run_command(["sudo", "ufw", "enable"], self.handle_enable_disable),
            activebackground="#2ecc71", 
            **button_style, 
            width=8
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        tk.Button(
            action_frame, 
            text="🛑 Disable", 
            bg="#c0392b", 
            fg=self.text_color,
            command=lambda: self.run_command(["sudo", "ufw", "disable"], self.handle_enable_disable),
            activebackground="#e74c3c", 
            **button_style, 
            width=8
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

    def _create_port_controls(self):
        """Create port management controls"""
        port_frame = tk.LabelFrame(
            self.left_panel, 
            text="Port Management", 
            bg=self.bg_color, 
            fg=self.accent_color, 
            font=("Arial", 11, "bold"), 
            padx=10, 
            pady=10
        )
        port_frame.pack(fill=tk.X, pady=10)
        
        entry_frame = tk.Frame(port_frame, bg=self.bg_color)
        entry_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            entry_frame, 
            text="Port:", 
            bg=self.bg_color, 
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=5)
        
        def validate_port(P):
            if P == "":
                return True
            return P.isdigit() and 0 <= int(P) <= 65535
        
        vcmd = (self.register(validate_port), '%P')
        self.port_entry = tk.Entry(
            entry_frame, 
            bg="#214c78", 
            fg=self.text_color,
            insertbackground=self.text_color, 
            relief=tk.FLAT,
            validate="key", 
            validatecommand=vcmd
        )
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=5)
        
        # First row for Allow/Deny buttons
        action_frame1 = tk.Frame(port_frame, bg=self.bg_color)
        action_frame1.pack(fill=tk.X, pady=(5, 0))
        
        button_style = {
            "font": ("Arial", 11),
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 8
        }
        
        # Allow button
        tk.Button(
            action_frame1, 
            text="➕ Allow", 
            bg="#27ae60", 
            fg=self.text_color, 
            command=self.handle_allow_port,
            activebackground="#2ecc71", 
            **button_style
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Deny button
        tk.Button(
            action_frame1, 
            text="🚫 Deny", 
            bg="#c0392b", 
            fg=self.text_color, 
            command=self.handle_deny_port,
            activebackground="#e74c3c", 
            **button_style
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # Second row for Reference button
        action_frame2 = tk.Frame(port_frame, bg=self.bg_color)
        action_frame2.pack(fill=tk.X, pady=(0, 5))
        
        # Reference button - now full width below the other buttons
        tk.Button(
            action_frame2, 
            text="📖 Port Reference", 
            bg=self.button_color, 
            fg=self.text_color, 
            command=self.show_ports_manual,
            activebackground=self.accent_color, 
            **button_style
        ).pack(fill=tk.X, expand=True, padx=2)
        
    def show_ports_manual(self):
        """Display a window with common ports information"""
        manual_window = tk.Toplevel(self)
        manual_window.title("Firewall Ports Reference")
        manual_window.geometry("500x400")
        manual_window.configure(bg=self.bg_color)
        manual_window.resizable(False, False)
        
        # Main container
        container = tk.Frame(manual_window, bg=self.bg_color, padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(container, text="Common Network Ports Reference", 
                font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 15))
        
        # Text widget for port information
        text_frame = tk.Frame(container, bg=self.bg_color)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text = tk.Text(text_frame, bg="#214c78", fg=self.text_color,
                      font=("Courier", 10), padx=10, pady=10, wrap=tk.WORD,
                      relief=tk.FLAT)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Port information data
        ports_info = """
        COMMON PORTS REFERENCE:
        
        HTTP:        80       (Web traffic - unencrypted)
        HTTPS:       443      (Web traffic - encrypted)
        SSH:         22       (Secure remote access)
        FTP:         21       (File transfers)
        FTPS:        990      (FTP over SSL)
        SFTP:        22       (SSH File Transfer)
        DNS:         53       (Domain Name System)
        SMTP:        25       (Email sending)
        POP3:        110      (Email retrieval)
        IMAP:        143      (Email management)
        MySQL:       3306     (Database)
        PostgreSQL:  5432     (Database)
        RDP:         3389     (Remote Desktop)
        VNC:         5900     (Remote control)
        SMB:         445      (File/print sharing)
        
        GAMING PORTS:
        Minecraft:   25565
        Steam:       27015-27030
        
        SECURITY NOTE:
        Only open ports you absolutely need.
        Close all ports when not in use.
        """
        
        text.insert(tk.END, ports_info)
        text.config(state=tk.DISABLED)  # Make it read-only
        
        # Close button
        close_btn = tk.Button(container, text="Close", 
                            command=manual_window.destroy,
                            bg=self.button_color, fg=self.text_color,
                            padx=20, pady=5)
        close_btn.pack(pady=(15, 0))

    def _create_network_controls(self):
        """Create network status controls"""
        network_frame = tk.LabelFrame(
            self.left_panel, 
            text="Network Status", 
            bg=self.bg_color, 
            fg=self.accent_color, 
            font=("Arial", 11, "bold"), 
            padx=10, 
            pady=10
        )
        network_frame.pack(fill=tk.X, pady=5)
        
        button_style = {
            "font": ("Arial", 11),
            "relief": tk.FLAT,
            "bd": 0,
            "cursor": "hand2",
            "padx": 15,
            "pady": 8
        }
        
        tk.Button(
            network_frame, 
            text="📡 Show Connections", 
            bg=self.button_color, 
            fg=self.text_color,
            command=lambda: self.run_command(["ss", "-tunap"], self.display_connections),
            activebackground=self.accent_color, 
            **button_style
        ).pack(fill=tk.X, pady=3)

    def _create_right_panel(self):
        """Create right output panel"""
        self.right_panel = tk.Frame(self.main_container, bg=self.bg_color)
        
        tk.Label(
            self.right_panel, 
            text="Console Output", 
            bg=self.bg_color, 
            fg=self.accent_color, 
            font=("Arial", 12, "bold"), 
            anchor="w"
        ).pack(fill=tk.X, padx=10, pady=5)
        
        self.output_text = tk.Text(
            self.right_panel, 
            bg="#214c78", 
            fg=self.text_color,
            font=("Courier", 10), 
            padx=10, 
            pady=10, 
            relief=tk.FLAT, 
            wrap=tk.WORD
        )
        
        # Configure text tags
        self.output_text.tag_configure("success", foreground="#2ecc71")
        self.output_text.tag_configure("warning", foreground="#f39c12")
        self.output_text.tag_configure("error", foreground="#e74c3c")
        self.output_text.tag_configure("info", foreground="#3498db")
        self.output_text.tag_configure("header", foreground="#f1c40f", font=("Courier", 10, "bold"))
            
        scrollbar = ttk.Scrollbar(
            self.right_panel, 
            command=self.output_text.yview
        )
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.main_container.add(self.right_panel)
        
        # Initial message
        self.output_text.insert(tk.END, "Welcome to Firewall & Network Monitor\n", "header")
        self.output_text.insert(tk.END, "Use the controls on the left to manage your firewall.\n")
        self.output_text.insert(tk.END, "Click 'Check Status' to view the current configuration.\n\n")

    def _test_command_execution(self):
        """Test if commands can be executed successfully"""
        def callback(output, error):
            if error:
                self.create_error_ui("Command execution failed")
                logger.log_event(f"Command test failed: {str(error)}")
        
        self.run_command(["sudo", "ufw", "--version"], callback)

    def run_command(self, command, callback):
        """Safely execute system command in thread"""
        if self.shutting_down:
            return
            
        def _execute():
            try:
                proc = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                try:
                    stdout, stderr = proc.communicate(timeout=10)
                    if proc.returncode == 0:
                        self.after(0, callback, stdout, None)
                    else:
                        error = subprocess.CalledProcessError(
                            proc.returncode, 
                            command, 
                            stdout, 
                            stderr
                        )
                        self.after(0, callback, None, error)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    self.after(0, callback, None, RuntimeError("Command timed out"))
                    
            except Exception as e:
                self.after(0, callback, None, e)
        
        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()

    def display_status(self, output, error):
        """Display firewall status"""
        self.output_text.delete(1.0, tk.END)
        if error:
            self.output_text.insert(tk.END, "ERROR RETRIEVING FIREWALL STATUS\n", "error")
            self.output_text.insert(tk.END, str(error.output if hasattr(error, 'output') else error))
            messagebox.showerror("Error", "Failed to retrieve firewall status")
        else:
            self.display_output(output)
            logger.log_event("Checked firewall status")

    def handle_enable_disable(self, output, error):
        """Handle enable/disable firewall commands"""
        if error:
            self.output_text.insert(tk.END, "ERROR MODIFYING FIREWALL STATE\n", "error")
            self.output_text.insert(tk.END, str(error.output if hasattr(error, 'output') else error))
            messagebox.showerror("Error", "Failed to modify firewall state")
        else:
            self.output_text.insert(tk.END, "Firewall state changed successfully\n", "success")
            self.run_command(["sudo", "ufw", "status"], self.display_status)
            logger.log_event("Changed firewall state")

    def handle_allow_port(self):
        """Handle port allowance"""
        port = self.port_entry.get()
        if port.isdigit():
            self.run_command(["sudo", "ufw", "allow", port], self.handle_port_change)
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid port number.")

    def handle_deny_port(self):
        """Handle port denial"""
        port = self.port_entry.get()
        if port.isdigit():
            self.run_command(["sudo", "ufw", "deny", port], self.handle_port_change)
        else:
            messagebox.showwarning("Invalid Input", "Please enter a valid port number.")

    def handle_port_change(self, output, error):
        """Handle port rule changes"""
        if error:
            self.output_text.insert(tk.END, "ERROR MODIFYING PORT RULE\n", "error")
            self.output_text.insert(tk.END, str(error.output if hasattr(error, 'output') else error))
            messagebox.showerror("Error", "Failed to modify port rule")
        else:
            self.output_text.insert(tk.END, "Port rule modified successfully\n", "success")
            self.run_command(["sudo", "ufw", "status"], self.display_status)
            logger.log_event("Modified port rule")

    def display_connections(self, output, error):
        """Display network connections"""
        self.output_text.delete(1.0, tk.END)
        if error:
            self.output_text.insert(tk.END, "ERROR RETRIEVING CONNECTIONS\n", "error")
            self.output_text.insert(tk.END, str(error.output if hasattr(error, 'output') else error))
            messagebox.showerror("Error", "Failed to retrieve network connections")
        else:
            self.output_text.insert(tk.END, "ACTIVE NETWORK CONNECTIONS\n", "header")
            self.display_output(output)
            logger.log_event("Viewed active network connections")

    def display_output(self, output):
        """Display output with syntax highlighting"""
        lines = output.split('\n')
        for line in lines:
            line = line + '\n'
            
            if "Status: active" in line:
                self.output_text.insert(tk.END, line, "success")
            elif "Status: inactive" in line:
                self.output_text.insert(tk.END, line, "warning")
            elif "ALLOW" in line:
                self.output_text.insert(tk.END, line, "success")
            elif "DENY" in line:
                self.output_text.insert(tk.END, line, "error")
            elif line.startswith("To") or "Action" in line or "Status" in line:
                self.output_text.insert(tk.END, line, "header")
            else:
                self.output_text.insert(tk.END, line)

    def destroy(self):
        """Clean up resources safely"""
        self.shutting_down = True
        super().destroy()
