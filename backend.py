import requests
from datetime import datetime
import pytz
from models import db, User

def create_user(email, is_admin=False):
    user = User(email=email, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()

def update_login_metadata(email, ip_address):
    user = User.query.get(email)
    geo = requests.get(f"https://ipapi.co/{ip_address}/json/").json()

    user.last_login_at = datetime.utcnow()
    user.last_login_ip = ip_address
    user.last_login_lat = geo.get("latitude")
    user.last_login_lon = geo.get("longitude")
    user.timezone = geo.get("timezone") or "America/Los_Angeles"

    db.session.commit()

def get_user_by_calendar_token(token):
    user = User.query.filter_by(calendar_token=token).first()
    return user.email if user else None

def generate_ical_for_user(email):
    user = User.query.get(email)
    timezone = user.timezone or "America/Los_Angeles"

    shift_start_utc = datetime(2025, 6, 6, 16, 0, 0, tzinfo=pytz.UTC)
    shift_end_utc = datetime(2025, 6, 6, 20, 0, 0, tzinfo=pytz.UTC)

    user_tz = pytz.timezone(timezone)
    shift_start_local = shift_start_utc.astimezone(user_tz)
    shift_end_local = shift_end_utc.astimezone(user_tz)

    start_str = shift_start_local.strftime("%Y%m%dT%H%M%S")
    end_str = shift_end_local.strftime("%Y%m%dT%H%M%S")

    return f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Chuck E Sync//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
SUMMARY:Sample Shift for {email}
DTSTART;TZID={timezone}:{start_str}
DTEND;TZID={timezone}:{end_str}
END:VEVENT
END:VCALENDAR
"""
