# routes/auth_routes.py
from flask import redirect, request, session, url_for, render_template, flash
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from app import app
from db import get_db
import pickle

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.readonly'
]

@app.route('/login')
def login():
    if not session.get('cookie_consent'):
        flash("You must accept cookies to log in.")
        return redirect(url_for('index'))

    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    session['state'] = state
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    people_service = build('people', 'v1', credentials=creds)
    profile = people_service.people().get(resourceName='people/me', personFields='emailAddresses').execute()
    email = profile['emailAddresses'][0]['value']

    session.permanent = True
    if session.get('cookie_consent'):
        session['user_email'] = email

    conn = get_db()
    conn.execute("REPLACE INTO users (email, token) VALUES (?, ?)", (email, pickle.dumps(creds)))
    conn.commit()

    is_admin = conn.execute("SELECT is_admin FROM users WHERE email = ?", (email,)).fetchone()['is_admin']
    return redirect(url_for('admin' if is_admin else 'success'))

@app.route('/accept_cookies', methods=['POST'])
def accept_cookies():
    session.permanent = True
    session['cookie_consent'] = True
    flash('Cookies enabled. You may now log in.')
    return redirect(url_for('index'))
