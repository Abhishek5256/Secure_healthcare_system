# Writes simple audit events to a local log file.

from datetime import datetime

LOG_FILE = "audit.log"


def log_event(username, action):
    """Append a timestamped audit entry to the audit log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] User: {username} | Action: {action}\n")