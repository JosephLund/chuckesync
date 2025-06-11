import os
import json

class Config:
    VERSION = "1.0.0"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key'
    GOOGLE_CLIENT_SECRET_FILE = 'credentials.json'
    GOOGLE_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/calendar'
    ]

    # Load credentials.json
    with open(GOOGLE_CLIENT_SECRET_FILE, 'r') as f:
        credentials = json.load(f)['google']['web']
        GOOGLE_CLIENT_ID = credentials['client_id']
        GOOGLE_CLIENT_SECRET = credentials['client_secret']
        GOOGLE_DISCOVERY_URL = credentials.get(
            'discovery_url',
            'https://accounts.google.com/.well-known/openid-configuration'
        )
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    f"sqlite:///{os.path.join(basedir, 'instance', 'chuckesync.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROTECTED_ADMIN_EMAIL = "josephtlund@gmail.com"
