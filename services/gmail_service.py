import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

class GmailService:
    def __init__(self, credentials_file, scopes):
        self.credentials_file = credentials_file
        self.scopes = scopes
        self.creds = None

    def authenticate(self):
        if os.path.exists('token_gmail.pickle'):
            with open('token_gmail.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                self.creds = flow.run_local_server(port=8080)
            with open('token_gmail.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        return build('gmail', 'v1', credentials=self.creds)