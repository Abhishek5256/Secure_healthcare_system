# audit.py
# This file stores audit logs for important user activity.

from datetime import datetime

LOG_FILE = "audit.log"


def log_event(username, action):
    # Write an audit event to the log file.
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] User: {username} | Action: {action}\n")