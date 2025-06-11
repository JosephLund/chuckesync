# commands.py

from flask import flash
from models import User, db
import os
from logger import LOG_FILE, log_event, get_logs

COMMANDS = {}

def command(name):
    def wrapper(func):
        COMMANDS[name] = func
        return func
    return wrapper

@command("clear_logs")
def clear_logs():
    open(LOG_FILE, 'w').close()
    return "✔ Logs cleared."

@command("show_logs")
def show_logs():
    return get_logs() or "(no logs)"

@command("delete_user")
def delete_user(email):
    user = User.get_user(email)
    if not user:
        return f"User '{email}' not found."
    db.session.delete(user)
    db.session.commit()
    return f"🗑 User '{email}' deleted."

@command("toggle_admin")
def toggle_admin(email):
    user = User.get_user(email)
    if not user:
        return f"User '{email}' not found."
    user.is_admin = not user.is_admin
    db.session.commit()
    return f"🔁 User '{email}' admin status set to {user.is_admin}."

@command("list_users")
def list_users():
    users = User.all_users()
    return "\n".join([f"{u.email} - {'Admin' if u.is_admin else 'User'}" for u in users])

@command("show_logs")
def show_logs():
    if not os.path.exists("server.log"):
        return "No log file found."
    with open("server.log", "r") as f:
        return f.read()

@command("show_user_logs")
def show_user_logs():
    if not os.path.exists("server.log"):
        return "No log file found."
    with open("server.log", "r") as f:
        lines = f.readlines()
    user_logs = [line for line in lines if '"user":' in line]
    return "".join(user_logs) or "No user-related logs found."

@command("show_general_logs")
def show_general_logs():
    if not os.path.exists("server.log"):
        return "No log file found."
    with open("server.log", "r") as f:
        lines = f.readlines()
    general_logs = [line for line in lines if '"user":' not in line]
    return "".join(general_logs) or "No general logs found."
# --- Test log entries ---

@command("log_info")
def log_info():
    log_event("This is a test info log entry", level="info")
    return "ℹ Test info log written."

@command("log_warning")
def log_warning():
    log_event("This is a test warning log entry", level="warning")
    return "⚠ Test warning log written."

@command("log_error")
def log_error():
    log_event("This is a test error log entry", level="error")
    return "❌ Test error log written."

@command("log_test_user")
def log_test_user():
    log_event("User triggered a test log", user="test@example.com", level="info")
    return "📄 Test log with user set."

@command("add_user")
def add_user(args):
    email = args.strip()
    if not email:
        return "Usage: add_user <email>"
    if User.get_user(email):
        return f"User {email} already exists."
    user = User(email=email)
    db.session.add(user)
    db.session.commit()
    return f"User {email} added."

@command("add_admin")
def add_admin(args):
    email = args.strip()
    if not email:
        return "Usage: add_admin <email>"
    if User.get_user(email):
        return f"User {email} already exists."
    user = User(email=email, is_admin=True)
    db.session.add(user)
    db.session.commit()
    return f"Admin user {email} added."


@command("cwd")
def get_cwd():
    return os.getcwd()

@command("ls")
def list_dir():
    return "\n".join(os.listdir("."))


@command("help")
def help_command():
    flash("Available commands: " + ", ".join(COMMANDS.keys()))
