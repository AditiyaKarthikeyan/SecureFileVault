import os
from datetime import datetime

LOG_FILE = "assets/logs/activity.log"

def ensure_log_dir():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_event(action, username="admin"):
    ensure_log_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{username}] {action}\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)

