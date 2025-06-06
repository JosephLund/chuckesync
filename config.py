import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key'
    GOOGLE_CLIENT_SECRET_FILE = 'credentials.json'
    GOOGLE_SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/calendar'
    ]