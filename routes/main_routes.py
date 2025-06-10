from flask import Blueprint, current_app, render_template, session, redirect, url_for, request, Response
from flask_sqlalchemy import SQLAlchemy
import backend
from models import User, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/admin')
def admin():
    logs = ""
    next_sync_epoch = 1721234567
    users = [u.to_dict() for u in User.all_users()]
    protected_email = current_app.config["PROTECTED_ADMIN_EMAIL"]
    return render_template('admin.html', logs=logs, next_sync_epoch=next_sync_epoch, users=users, protected_email=protected_email)

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