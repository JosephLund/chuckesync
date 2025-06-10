from flask import Blueprint, redirect, url_for, session, request
from models import User
import backend
import json
import requests
import os
from oauthlib.oauth2 import WebApplicationClient
from config import Config

auth_bp = Blueprint('auth', __name__)

# OAuth client setup
client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

# Helper to get Google's provider configuration
def get_google_provider_cfg():
    return requests.get(Config.GOOGLE_DISCOVERY_URL).json()

@auth_bp.route("/login/google")
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route("/login/google/callback")
def google_callback():
    code = request.args.get("code")

    with open('credentials.json') as f:
        credentials = json.load(f)
        admin_emails = credentials.get("admin_emails", [])
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(Config.GOOGLE_CLIENT_ID, Config.GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(token_response.text)

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    userinfo = userinfo_response.json()

    if not userinfo.get("email_verified"):
        return "User email not available or not verified by Google.", 400

    user_email = userinfo["email"]
    is_admin = user_email in admin_emails
    print(User.get_user(user_email))
    if not User.get_user(user_email):
        backend.create_user(user_email, is_admin)

    session['user_email'] = user_email
    user = User.get_user(user_email)
    session['is_admin'] = user.is_admin

    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    backend.update_login_metadata(user_email, ip_address)

    return redirect(url_for('main.dashboard'))

# Apple OAuth (placeholder)
@auth_bp.route('/login/apple')
def apple_login():
    return "Apple OAuth flow goes here"

@auth_bp.route('/login/apple/callback')
def apple_callback():
    return "Apple OAuth callback processing goes here"
