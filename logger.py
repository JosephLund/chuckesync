# logger.py
import os

LOG_FILE = 'server.log'

def log_error(message):
    with open(LOG_FILE, 'a') as f:
        f.write(f'{message}\n')

def get_logs():
    if not os.path.exists(LOG_FILE):
        return ''
    with open(LOG_FILE, 'r') as f:
        return f.read()