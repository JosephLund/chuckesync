from datetime import datetime
import os
import threading
import time
import pickle
import base64
from models import get_db, User, Store, UserStore, Shift, db
from googleapiclient.discovery import build
from utils.schedule_parser import parse_schedule
from logger import log_event

_sync_thread_started = False

def background_sync_users():
    global _sync_thread_started
    if _sync_thread_started:
        log_event("[SYNC] Background sync thread already running. Skipping duplicate.", level="info")
        return

    _sync_thread_started = True

    def sync_loop():
        while True:
            log_event("[SYNC] Starting periodic user sync...", level="info")
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
                        log_event(f"No new schedule for {email}. Skipping.", user=email, level="info")
                        continue

                    msg = gmail.users().messages().get(userId='me', id=latest_msg_id).execute()

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

                            shifts, store_list = parse_schedule(pdf_path)

                            user_obj = User.get_user(email)

                            # Store linking
                            store_id_map = {}
                            for number, name in store_list:
                                store = Store.query.filter_by(number=number).first()
                                if not store:
                                    store = Store(number=number, name=name)
                                    db.session.add(store)
                                    db.session.commit()

                                store_id_map[number] = store.id

                                if not UserStore.query.filter_by(user_email=user_obj.email, store_id=store.id).first():
                                    link = UserStore(user_email=user_obj.email, store_id=store.id)
                                    db.session.add(link)
                            db.session.commit()

                            # Shift insertion & calendar sync
                            for date_str, start, end in shifts:
                                try:
                                    shift_date = datetime.strptime(date_str, "%m/%d/%Y").date()
                                    start_dt = datetime.strptime(f"{date_str} {start}", "%m/%d/%Y %H:%M")
                                    end_dt = datetime.strptime(f"{date_str} {end}", "%m/%d/%Y %H:%M")

                                    # For now, assume first store if multiple (can improve later)
                                    store_id = list(store_id_map.values())[0]

                                    # Check for duplicate shift
                                    existing_shift = Shift.query.filter_by(
                                        user_email=email,
                                        store_id=store_id,
                                        date=shift_date,
                                        start_time=start_dt.time()
                                    ).first()

                                    if existing_shift:
                                        log_event(f"Shift already exists for {email} on {shift_date}", user=email, level="info")
                                        continue

                                    # Save shift to DB
                                    new_shift = Shift(
                                        user_email=email,
                                        store_id=store_id,
                                        date=shift_date,
                                        start_time=start_dt.time(),
                                        end_time=end_dt.time()
                                    )
                                    db.session.add(new_shift)
                                    db.session.commit()

                                    # Calendar duplicate check
                                    existing_events = calendar.events().list(
                                        calendarId='primary',
                                        timeMin=start_dt.isoformat(),
                                        timeMax=end_dt.isoformat(),
                                        q='Chuck E. Cheese Shift',
                                        singleEvents=True
                                    ).execute()

                                    if existing_events.get('items'):
                                        log_event(f"Event already exists in calendar for {start_dt} - skipping.", user=email, level="info")
                                        continue

                                    # Insert into calendar
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
                                    calendar.events().insert(calendarId='primary', body=event).execute()
                                    log_event(f"Event added: {start_dt} to {end_dt}", user=email, level="info")

                                except Exception as calendar_error:
                                    log_event(f"Event insert failed: {calendar_error}", user=email, level="error")

                            # Mark email synced
                            conn.execute("UPDATE users SET last_synced_id = ? WHERE email = ?", (latest_msg_id, email))
                            conn.commit()
                            log_event("Events added to calendar", user=email, level="info")
                            break

                except Exception as e:
                    log_event(f"Failed sync: {e}", user=email, level="error")

            time.sleep(1800)

    thread = threading.Thread(target=sync_loop, daemon=True)
    thread.start()
    log_event("[SYNC] Background sync thread started.", level="info")
