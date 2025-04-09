import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

# Ensure the database directory exists
DB_DIR = "assets/database"
DB_PATH = os.path.join(DB_DIR, "secure_vault.db")

# Database schema version
SCHEMA_VERSION = 2

def hash_password(password, salt=None):
    """Hash a password with a salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Combine password and salt, then hash
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    return password_hash, salt

def ensure_db_exists():
    """Create database directory and tables if they don't exist"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create version table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS db_version (
        version INTEGER PRIMARY KEY
    )
    ''')
    
    # Get current version
    cursor.execute("SELECT version FROM db_version")
    result = cursor.fetchone()
    current_version = result[0] if result else 0
    
    # Create or update schema as needed
    if current_version < 1:
        # Initial schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            totp_secret TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS secure_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            message_text TEXT,
            file_path TEXT,
            sent_at TEXT NOT NULL,
            read_at TEXT,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (recipient_id) REFERENCES users (id)
        )
        ''')
        
        # Check if admin user exists before inserting
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            # Create default admin user with fixed TOTP secret
            password_hash, salt = hash_password("admin123")
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute(
                "INSERT INTO users (username, password_hash, salt, full_name, email, totp_secret, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("admin", password_hash, salt, "Administrator", "admin@securevault.com", "HX3YB5DQOIZV2ZLZ", created_at)
            )
        
        current_version = 1
    
    if current_version < 2:
        # Schema version 2 adds permissions columns
        try:
            # Check if columns exist before adding them
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'account_type' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN account_type TEXT DEFAULT 'standard'")
            if 'can_access_firewall' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN can_access_firewall INTEGER DEFAULT 0")
            if 'can_access_logs' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN can_access_logs INTEGER DEFAULT 0")
            
            # Update admin user with permissions if it exists
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            admin_exists = cursor.fetchone()
            
            if admin_exists:
                cursor.execute(
                    "UPDATE users SET account_type = 'admin', can_access_firewall = 1, can_access_logs = 1 "
                    "WHERE username = 'admin'"
                )
            
            current_version = 2
        except sqlite3.OperationalError as e:
            print(f"Error updating schema: {e}")
    
    # Update version if needed
    if current_version > 0:
        cursor.execute("DELETE FROM db_version")  # Clear existing version first
        cursor.execute("INSERT INTO db_version (version) VALUES (?)", (current_version,))
    else:
        cursor.execute("INSERT INTO db_version (version) VALUES (?)", (current_version,))
    
    conn.commit()
    conn.close()

def register_user(username, password, full_name, email, totp_secret):
    """Register a new user"""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if username already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False
    
    # Hash the password
    password_hash, salt = hash_password(password)
    
    # Insert the new user
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO users (username, password_hash, salt, full_name, email, totp_secret, created_at, account_type) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (username, password_hash, salt, full_name, email, totp_secret, created_at, 'standard')
    )
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return True

def authenticate_user(username, password):
    """Authenticate a user by username and password"""
    ensure_db_exists()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash, salt, totp_secret FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    if result:
        user_id, stored_hash, salt, totp_secret = result
        
        # Hash the provided password with the same salt
        calculated_hash, _ = hash_password(password, salt)
        
        if calculated_hash == stored_hash:
            # Update last login time
            last_login = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (last_login, user_id))
            conn.commit()
            conn.close()
            return user_id, totp_secret
    
    conn.close()
    return None, None

def get_user_profile(user_id):
    """Get user profile data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT username, full_name, email, created_at, last_login, account_type, can_access_firewall, can_access_logs "
        "FROM users WHERE id = ?", 
        (user_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "username": result[0],
            "full_name": result[1],
            "email": result[2],
            "created_at": result[3],
            "last_login": result[4],
            "account_type": result[5],
            "can_access_firewall": bool(result[6]),
            "can_access_logs": bool(result[7])
        }
    
    return None

def log_user_activity(user_id, action, details=None):
    """Log user activity for analytics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO user_activity (user_id, action, timestamp, details) VALUES (?, ?, ?, ?)",
        (user_id, action, timestamp, details)
    )
    
    conn.commit()
    conn.close()
    return True

def get_user_activity(user_id, limit=20):
    """Get recent user activity"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT action, timestamp, details FROM user_activity "
        "WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", 
        (user_id, limit)
    )
    
    activity = [{"action": row[0], "timestamp": row[1], "details": row[2]} 
               for row in cursor.fetchall()]
    conn.close()
    
    return activity

def get_all_users():
    """Get all users for admin panel"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, full_name, email, account_type, can_access_firewall, can_access_logs "
        "FROM users ORDER BY username"
    )
    
    users = [{"id": row[0], "username": row[1], "full_name": row[2], "email": row[3], 
              "account_type": row[4], "can_access_firewall": bool(row[5]), "can_access_logs": bool(row[6])} 
             for row in cursor.fetchall()]
    conn.close()
    
    return users

def update_user_permissions(user_id, firewall_access, logs_access):
    """Update user permissions for an existing user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE users SET can_access_firewall = ?, can_access_logs = ? WHERE id = ?",
        (int(firewall_access), int(logs_access), user_id)
    )
    
    conn.commit()
    conn.close()
    return True

def save_secure_message(sender_id, recipient_id, message_text, file_path=None):
    """Save a secure message or file share between users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "INSERT INTO secure_messages (sender_id, recipient_id, message_text, file_path, sent_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (sender_id, recipient_id, message_text, file_path, sent_at)
    )
    
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return message_id

def get_user_messages(user_id, direction="incoming"):
    """Get messages for a user (incoming or outgoing)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if direction == "incoming":
        query = """
            SELECT m.id, m.sender_id, u.username as sender_name, 
                   m.message_text, m.file_path, m.sent_at, m.read_at
            FROM secure_messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.recipient_id = ?
            ORDER BY m.sent_at DESC
        """
        cursor.execute(query, (user_id,))
    else:
        query = """
            SELECT m.id, m.recipient_id, u.username as recipient_name, 
                   m.message_text, m.file_path, m.sent_at, m.read_at
            FROM secure_messages m
            JOIN users u ON m.recipient_id = u.id
            WHERE m.sender_id = ?
            ORDER BY m.sent_at DESC
        """
        cursor.execute(query, (user_id,))
    
    if direction == "incoming":
        messages = [{"id": row[0], "sender_id": row[1], "sender_name": row[2], 
                    "message": row[3], "file_path": row[4], "sent_at": row[5], "read_at": row[6]} 
                   for row in cursor.fetchall()]
    else:
        messages = [{"id": row[0], "recipient_id": row[1], "recipient_name": row[2], 
                    "message": row[3], "file_path": row[4], "sent_at": row[5], "read_at": row[6]} 
                   for row in cursor.fetchall()]
    
    conn.close()
    return messages

def mark_message_as_read(message_id):
    """Mark a message as read"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    read_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE secure_messages SET read_at = ? WHERE id = ?", (read_at, message_id))
    
    conn.commit()
    conn.close()
    return True
