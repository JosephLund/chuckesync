# routes/user_routes.py
from flask import render_template, session, redirect, url_for, flash
from app import app
from db import get_db

@app.route('/success')
def success():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('index'))
    return render_template('success.html', email=email)

@app.route('/remove_me', methods=['POST'])
def remove_me():
    email = session.get('user_email')
    conn = get_db()
    conn.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    flash('You have been removed from automation.')
    return redirect(url_for('index'))
