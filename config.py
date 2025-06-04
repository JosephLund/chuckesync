import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key'

    # Database config (SQLite for now)
    DATABASE_URI = 'sqlite:///chuckesync.db'

    # OAuth credentials
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # You can also later add Apple keys, email, etc.
