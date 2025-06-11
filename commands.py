# commands.py

from datetime import datetime, timedelta, time
import random
from flask import flash
from models import Shift, Store, User, UserStore, db
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
    if isinstance(args, list):
        email = args
    else:
        email = args.split()
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
    if isinstance(args, list):
        email = args
    else:
        email = args.split()
    if not email:
        return "Usage: add_admin <email>"
    if User.get_user(email):
        return f"User {email} already exists."
    user = User(email=email, is_admin=True)
    db.session.add(user)
    db.session.commit()
    return f"Admin user {email} added."

@command("add_fake_shifts")
def add_fake_shifts():
    """Generate fake shifts for logged in admin for current week."""
    from flask import session
    email = session.get('user_email')
    if not email:
        return "No user logged in."

    user = User.get_user(email)
    if not user:
        return f"User '{email}' not found."

    # Check if user has any stores linked
    user_stores = UserStore.query.filter_by(user_email=email).all()
    if not user_stores:
        # Create a default store if none exist
        store = Store(number="9999", name="Fake Testing Store")
        db.session.add(store)
        db.session.commit()
        link = UserStore(user_email=email, store_id=store.id)
        db.session.add(link)
        db.session.commit()
        user_stores = [link]

    store_id = user_stores[0].store_id

    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())

    shifts_added = 0

    for i in range(7):
        shift_date = monday + timedelta(days=i)
        start_hour = random.randint(8, 14)
        start_minute = random.choice([0, 30])
        start_time = time(start_hour, start_minute)
        end_time = time(start_hour + 8, start_minute)

        # Prevent duplicates
        existing = Shift.query.filter_by(
            user_email=email,
            store_id=store_id,
            date=shift_date,
            start_time=start_time
        ).first()

        if existing:
            continue

        shift = Shift(
            user_email=email,
            store_id=store_id,
            date=shift_date,
            start_time=start_time,
            end_time=end_time
        )
        db.session.add(shift)
        shifts_added += 1

    db.session.commit()
    return f"✔ Added {shifts_added} fake shifts for {email}."

@command("add_store_to_user")
def add_store_to_user(args):
    """Usage: add_store_to_user <user_email> <store_number>"""
    if isinstance(args, list):
        parts = args
    else:
        parts = args.split()
    if len(parts) != 2:
        return "Usage: add_store_to_user <user_email> <store_number>"

    email, store_number = parts
    user = User.get_user(email)
    if not user:
        return f"User '{email}' not found."

    store = Store.query.filter_by(number=store_number).first()
    if not store:
        store = Store(number=store_number, name=f"Store {store_number}")
        db.session.add(store)
        db.session.commit()

    link = UserStore.query.filter_by(user_email=email, store_id=store.id).first()
    if link:
        return f"Store {store_number} already assigned to {email}."

    db.session.add(UserStore(user_email=email, store_id=store.id))
    db.session.commit()

    return f"✔ Store {store_number} assigned to {email}."

@command("remove_store_from_user")
def remove_store_from_user(args):
    """Usage: remove_store_from_user <user_email> <store_number>"""
    if isinstance(args, list):
        parts = args
    else:
        parts = args.split()
    if len(parts) != 2:
        return "Usage: remove_store_from_user <user_email> <store_number>"

    email, store_number = parts
    user = User.get_user(email)
    if not user:
        return f"User '{email}' not found."

    store = Store.query.filter_by(number=store_number).first()
    if not store:
        return f"Store {store_number} not found."

    link = UserStore.query.filter_by(user_email=email, store_id=store.id).first()
    if not link:
        return f"{email} not linked to store {store_number}."

    db.session.delete(link)
    db.session.commit()

    return f"✔ Store {store_number} removed from {email}."

@command("delete_user_shifts")
def delete_shifts_by_user_and_date(args):
    """Usage: delete_user_shifts <email> <start_date> <end_date>"""
    if isinstance(args, list):
        parts = args
    else:
        parts = args.split()
    if len(parts) != 3:
        return "Usage: delete_user_shifts <email> <start_date> <end_date>"

    email, start_str, end_str = parts

    user = User.get_user(email)
    if not user:
        return f"User '{email}' not found."

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        return "Invalid date format. Use YYYY-MM-DD."

    deleted_count = Shift.query.filter(
        Shift.user_email == email,
        Shift.date >= start_date,
        Shift.date <= end_date
    ).delete(synchronize_session=False)

    db.session.commit()

    return f"🗑 Deleted {deleted_count} shifts for {email} between {start_str} and {end_str}."


@command("cwd")
def get_cwd():
    return os.getcwd()

@command("ls")
def list_dir():
    return "\n".join(os.listdir("."))


@command("help")
def help_command():
    flash("Available commands: " + ", ".join(COMMANDS.keys()))
