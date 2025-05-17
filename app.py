# app.py
from flask import Flask
from datetime import timedelta
import os

app = Flask(__name__)

app.secret_key = os.urandom(24)
app.secret_key = 'sklebjoezeus'
app.permanent_session_lifetime = timedelta(days=30)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
