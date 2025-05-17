import os
import base64
import pickle
from datetime import datetime
from app import app

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES for Gmail and Calendar
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/calendar']

def authenticate_gmail():
    creds = None
    if os.path.exists('token_gmail.pickle'):
        with open('token_gmail.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token_gmail.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def authenticate_calendar():
    creds = None
    if os.path.exists('token_calendar.pickle'):
        with open('token_calendar.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token_calendar.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def get_schedule_pdf(gmail_service):
    results = gmail_service.users().messages().list(userId='me', q="from:nbo-noreply@alohaenterprise.com filename:pdf").execute()
    messages = results.get('messages', [])
    if not messages:
        print("No schedule found.")
        return None

    msg = gmail_service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    parts = msg['payload']['parts']
    for part in parts:
        if part['filename'].endswith('.pdf'):
            attachment_id = part['body']['attachmentId']
            attachment = gmail_service.users().messages().attachments().get(userId='me', messageId=msg['id'], id=attachment_id).execute()
            data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            with open('schedule.pdf', 'wb') as f:
                f.write(data)
            return 'schedule.pdf'
    return None

def parse_schedule(pdf_path):
    from datetime import datetime, timedelta
    import pdfplumber
    import re

    def normalize_ampm(t):
        return t + 'm' if t and t[-1] in ['a', 'p'] else t

    shifts = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            # Extract "Week of" date
            week_match = re.search(r'Week of ([A-Za-z]+\s+\d{1,2},\s+\d{4})', text)
            if not week_match:
                continue
            week_start = datetime.strptime(week_match.group(1), "%B %d, %Y")

            # Generate date list: Mon–Sun
            full_dates = [
                (week_start + timedelta(days=i)).strftime("%m/%d/%Y")
                for i in range(7)
            ]

            # Extract tables
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row and len(row) == 7 and any(cell.strip() for cell in row):
                        # Found candidate shift row with 7 columns
                        for i, cell in enumerate(row):
                            date = full_dates[i]
                            if cell and "-" in cell:
                                match = re.match(r'(\d{1,2}:\d{2}[ap])-(\d{1,2}:\d{2}[ap])', cell.strip())
                                if match:
                                    start = normalize_ampm(match.group(1))
                                    end = normalize_ampm(match.group(2))
                                    try:
                                        start_24 = datetime.strptime(start, "%I:%M%p").strftime("%H:%M")
                                        end_24 = datetime.strptime(end, "%I:%M%p").strftime("%H:%M")
                                        shifts.append((date, start_24, end_24))
                                    except ValueError:
                                        shifts.append((date, None, None))
                                else:
                                    shifts.append((date, None, None))
                            else:
                                shifts.append((date, None, None))
                        return [s for s in shifts if s[1] and s[2]]  # Only return working days

    print("No valid shift data found.")
    return []

def create_calendar_events(calendar_service, shifts):
    calendar_id = 'primary'
    for date_str, start, end in shifts:
        start_dt = datetime.strptime(f"{date_str} {start}", "%m/%d/%Y %H:%M")
        end_dt = datetime.strptime(f"{date_str} {end}", "%m/%d/%Y %H:%M")

        event = {
            'summary': 'Chuck E. Cheese Shift',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
        }
        calendar_service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Added shift: {start_dt} - {end_dt}")

def main():
    gmail = authenticate_gmail()
    calendar = authenticate_calendar()

    pdf_path = get_schedule_pdf(gmail)
    if not pdf_path:
        print("No PDF found.")
        return

    shifts = parse_schedule(pdf_path)
    if not shifts:
        print("No shifts found.")
        return

    create_calendar_events(calendar, shifts)

if __name__ == "__main__":
    main()
