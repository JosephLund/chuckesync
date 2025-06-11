import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'server.log')

def log_event(message, level='INFO', user=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level.upper(),
        "message": message
    }
    if user:
        entry["user"] = user

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')

def get_logs():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def get_logs_for_user(user_email):
    return [log for log in get_logs() if log.get('user') == user_email]