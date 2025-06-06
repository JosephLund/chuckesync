from flask import Blueprint, redirect, render_template, session, url_for
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', current_year=datetime.now().year)
@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/admin')
def admin():
    return render_template('admin.html', current_year=datetime.now().year)

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')