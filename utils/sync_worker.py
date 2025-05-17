from datetime import datetime
import os
import threading
import time
import pickle
import base64
from db import get_db
from googleapiclient.discovery import build
from utils.schedule_parser import parse_schedule
from flask import flash
import logging

_sync_thread_started = False

def background_sync_users():
    global _sync_thread_started
    if _sync_thread_started:
        logging.info("[SYNC] Background sync thread already running. Skipping duplicate.")
        return

    _sync_thread_started = True

    def sync_loop():
        while True:
            logging.info("[SYNC] Starting periodic user sync...")
            conn = get_db()
            users = conn.execute("SELECT email, token, last_synced_id FROM users").fetchall()
            for user in users:
                email = user['email']
                creds = pickle.loads(user['token'])
                try:
                    gmail = build('gmail', 'v1', credentials=creds)
                    calendar = build('calendar', 'v3', credentials=creds)

                    messages = gmail.users().messages().list(
                        userId='me',
                        q="from:nbo-noreply@alohaenterprise.com filename:pdf",
                        maxResults=1
                    ).execute().get('messages', [])

                    if not messages:
                        continue

                    latest_msg_id = messages[0]['id']

                    if user['last_synced_id'] is not None and latest_msg_id == user['last_synced_id']:
                        logging.info(f"[SYNC] No new schedule for {email}. Skipping.")
                        continue

                    msg = gmail.users().messages().get(
                        userId='me', id=latest_msg_id
                    ).execute()

                    parts = msg['payload'].get('parts', [])
                    for part in parts:
                        filename = part.get('filename')
                        if filename and filename.endswith('.pdf'):
                            body = part.get('body', {})
                            data = body.get('data')

                            if not data and 'attachmentId' in body:
                                attachment = gmail.users().messages().attachments().get(
                                    userId='me', messageId=msg['id'], id=body['attachmentId']
                                ).execute()
                                data = attachment.get('data')

                            if not data:
                                continue

                            decoded = base64.urlsafe_b64decode(data.encode('utf-8'))
                            pdf_path = os.path.join('uploads', f"{email.replace('@', '_')}_latest.pdf")
                            with open(pdf_path, 'wb') as f:
                                f.write(decoded)

                            shifts = parse_schedule(pdf_path)
                            for date_str, start, end in shifts:
                                try:
                                    # Format datetime safely
                                    start_dt = datetime.strptime(f"{date_str} {start}", "%m/%d/%Y %H:%M")
                                    end_dt = datetime.strptime(f"{date_str} {end}", "%m/%d/%Y %H:%M")

                                    event = {
                                        'summary': 'Chuck E. Cheese Shift',
                                        'start': {
                                            'dateTime': start_dt.isoformat(),
                                            'timeZone': 'America/Los_Angeles'
                                        },
                                        'end': {
                                            'dateTime': end_dt.isoformat(),
                                            'timeZone': 'America/Los_Angeles'
                                        }
                                    }
                                    # calendar.events().insert(calendarId='primary', body=event).execute()
                                    logging.info(f"[SYNC] Event added: {start_dt} to {end_dt} for {email}")
                                except Exception as calendar_error:
                                    logging.error(f"[SYNC ERROR] Event insert failed for {email}: {calendar_error}")

                            conn.execute("UPDATE users SET last_synced_id = ? WHERE email = ?", (latest_msg_id, email))
                            conn.commit()
                            logging.info(f"[SYNC] Events added to calendar for {email}")
                            break
                except Exception as e:
                    logging.exception(f"[SYNC ERROR] Failed for {email}: {e}")
            time.sleep(1800)  # 30 minutes

    thread = threading.Thread(target=sync_loop, daemon=True)
    thread.start()
    logging.info("[SYNC] Background sync thread started.")