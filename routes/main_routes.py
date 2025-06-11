from datetime import datetime
from flask import Blueprint, current_app, flash, render_template, session, redirect, url_for, request, Response
from flask_sqlalchemy import SQLAlchemy
import backend
from models import User, db
from logger import get_logs, log_event
from utils.location import get_ip_info

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    user_email = session.get("user_email")
    user = User.get_user(user_email)

    if user:
        # Determine IP
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        if user.location_tracking_enabled:
            location = get_ip_info(ip)
            user.last_login_lat = location["lat"]
            user.last_login_lon = location["lon"]
            user.timezone = location["timezone"]
        else:
            user.last_login_lat = None
            user.last_login_lon = None
            user.timezone = "America/Los_Angeles"

        # ✅ Commit updates regardless of setting
        db.session.commit()

        # ✅ Log the access
        log_event("User accessed dashboard", user=user.email, level="info")

    else:
        flash("You must be logged in to access the dashboard.", "warning")
        return render_template('index.html')

    return render_template("dashboard.html", user=user)

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route("/toggle_location_tracking", methods=["POST"])
def toggle_location_tracking():
    email = session.get("user_email")
    user = User.get_user(email)
    if user:
        user.location_tracking_enabled = "location_tracking_enabled" in request.form
        db.session.commit()
        flash("Location analytics setting updated.")
    return redirect(url_for("main.dashboard"))

@main_bp.route('/admin')
def admin():
    
    logs = get_logs()
    next_sync_epoch = 1721234567
    users = [u.to_dict() for u in User.all_users()]
    user_timezones = {user["email"]: user.get("timezone", "UTC") or "UTC" for user in users}
    protected_email = current_app.config["PROTECTED_ADMIN_EMAIL"]
    return render_template('admin.html', logs=logs, next_sync_epoch=next_sync_epoch, users=users, protected_email=protected_email, user_timezones=user_timezones)

@main_bp.route("/accept_cookies", methods=["POST"])
def accept_cookies():
    session['cookie_consent'] = True
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@main_bp.route('/calendar/<token>.ics')
def calendar_feed(token):
    user_email = backend.get_user_by_calendar_token(token)
    if not user_email:
        return "Calendar feed not found", 404

    ical_data = backend.generate_ical_for_user(user_email)
    return Response(ical_data, mimetype='text/calendar')
