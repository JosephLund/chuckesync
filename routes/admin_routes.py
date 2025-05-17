# routes/admin_routes.py

from flask import jsonify, render_template, session, redirect, url_for, flash, request, g
from app import app
from db import get_db
from logger import get_logs, log_error
import pickle, base64, os
from googleapiclient.discovery import build
import logging
from template_generator import next_sync_epoch

from utils.schedule_parser import parse_schedule
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.before_request
@app.before_request
def load_user_admin_status():
    g.is_admin = False
    session['is_admin'] = False
    user_email = session.get('user_email')
    if user_email:
        conn = get_db()
        row = conn.execute('SELECT is_admin FROM users WHERE email = ?', (user_email,)).fetchone()
        if row and row['is_admin']:
            g.is_admin = True
            session['is_admin'] = True

@app.route('/admin')
def admin():
    if not g.is_admin:
        return "Unauthorized", 403

    conn = get_db()
    users = conn.execute('SELECT email, is_admin FROM users').fetchall()
    logs = get_logs()
    return render_template('admin.html', users=users, logs=logs, next_sync_epoch=int(next_sync_epoch))

@app.route('/delete_user/<email>', methods=['POST'])
def delete_user(email):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE email = ?', (email,))
    conn.commit()
    return redirect(url_for('admin'))

@app.route('/test_user/<email>', methods=['POST'])
def test_user(email):
    logging.info(f"[TEST START] Initiating test for user: {email}")

    conn = get_db()
    row = conn.execute('SELECT token FROM users WHERE email = ?', (email,)).fetchone()
    if not row:
        logging.warning(f"[TEST] User not found in DB: {email}")
        flash('User not found')
        return redirect(url_for('admin'))

    try:
        creds = pickle.loads(row['token'])
        logging.info(f"[TEST] Credentials loaded for {email}")

        gmail = build('gmail', 'v1', credentials=creds)
        logging.info(f"[TEST] Gmail service built for {email}")

        messages = gmail.users().messages().list(
            userId='me',
            q="from:nbo-noreply@alohaenterprise.com filename:pdf"
        ).execute().get('messages', [])

        if not messages:
            logging.info(f"[TEST] No schedule email found for {email}")
            flash('No recent schedule found')
            return redirect(url_for('admin'))

        logging.info(f"[TEST] Found {len(messages)} message(s) for {email}")

        msg = gmail.users().messages().get(
            userId='me',
            id=messages[0]['id']
        ).execute()

        parts = msg['payload'].get('parts', [])
        logging.info(f"[TEST] Message parts count: {len(parts)}")

        for part in parts:
            filename = part.get('filename')
            logging.debug(f"[TEST] Inspecting part: {filename}")

            if filename and filename.endswith('.pdf'):
                body = part.get('body', {})
                body_data = body.get('data')
                attachment_id = body.get('attachmentId')

                if not body_data and not attachment_id:
                    logging.warning(f"[TEST] No data or attachment ID found in body for {filename}")
                    continue

                try:
                    if not body_data and attachment_id:
                        logging.info(f"[TEST] Fetching attachment data for {filename}")
                        attachment = gmail.users().messages().attachments().get(
                            userId='me',
                            messageId=msg['id'],
                            id=attachment_id
                        ).execute()
                        body_data = attachment.get('data')

                    if not body_data:
                        logging.warning(f"[TEST] Attachment data still missing for {filename}")
                        continue

                    data = base64.urlsafe_b64decode(body_data.encode('utf-8'))
                    pdf_path = os.path.join(UPLOAD_FOLDER, f"{email.replace('@', '_')}.pdf")

                    with open(pdf_path, 'wb') as f:
                        f.write(data)

                    logging.info(f"[TEST] PDF written to {pdf_path}")
                    flash(f'Test run completed for {email}')
                    pdf_found = True
                    break
                except Exception as decode_error:
                    logging.exception(f"[TEST ERROR] Failed to decode or write PDF for {email}: {decode_error}")
                    flash(f"Error saving PDF for {email}")
                    break


        if not pdf_found:
            logging.warning(f"[TEST] No PDF attachment found for message related to {email}")
            flash("No PDF attachment found in the email.")
    except Exception as e:
        error_msg = f"[TEST ERROR] {email}: {str(e)}"
        logging.exception(error_msg)
        log_error(error_msg)
        flash('An error occurred. See admin logs.')

    return redirect(url_for('admin'))

@app.route('/make_admin/<email>', methods=['POST'])
def make_admin(email):
    conn = get_db()
    conn.execute("UPDATE users SET is_admin = 1 WHERE email = ?", (email,))
    conn.commit()
    return redirect(url_for('admin'))

@app.route('/remove_admin/<email>', methods=['POST'])
def remove_admin(email):
    conn = get_db()
    conn.execute("UPDATE users SET is_admin = 0 WHERE email = ?", (email,))
    conn.commit()
    return redirect(url_for('admin'))
@app.route('/exec_command', methods=['POST'])
def exec_command():
    if session.get('user_email') != 'josephtlund@gmail.com':
        return jsonify({'error': 'Unauthorized'}), 403
    try:
        command = request.form.get('command')
        output = str(eval(command))  # Dangerous in prod — safe only in controlled local admin panel
        logging.info(f"EXEC >>> {command} => {output}")
        return redirect(url_for('admin'))
    except Exception as e:
        logging.exception(f"EXEC ERROR: {e}")
        return redirect(url_for('admin'))
    
@app.route('/sync_user_calendar/<email>', methods=['POST'])
def sync_user_calendar_route(email):
    success = sync_user_calendar(email)  # call your sync logic

    if success:
        flash(f"Sync complete for {email}", "success")
    else:
        flash(f"Sync failed for {email}. See logs.", "danger")

    return redirect(url_for('admin'))

def sync_user_calendar(email):
    logging.info(f"[SYNC] Starting calendar sync for {email}")
    conn = get_db()
    row = conn.execute('SELECT token FROM users WHERE email = ?', (email,)).fetchone()

    if not row:
        logging.warning(f"[SYNC] No credentials found for {email}")
        return False

    try:
        creds = pickle.loads(row['token'])
        gmail = build('gmail', 'v1', credentials=creds)
        calendar = build('calendar', 'v3', credentials=creds)

        messages = gmail.users().messages().list(
            userId='me',
            q="from:nbo-noreply@alohaenterprise.com filename:pdf"
        ).execute().get('messages', [])

        if not messages:
            logging.warning(f"[SYNC] No email found for {email}")
            return False

        msg = gmail.users().messages().get(userId='me', id=messages[0]['id']).execute()
        parts = msg['payload'].get('parts', [])

        for part in parts:
            filename = part.get('filename')
            if filename and filename.endswith('.pdf'):
                body = part.get('body', {})
                data = body.get('data')

                if not data and 'attachmentId' in body:
                    attachment = gmail.users().messages().attachments().get(
                        userId='me',
                        messageId=msg['id'],
                        id=body['attachmentId']
                    ).execute()
                    data = attachment.get('data')

                if not data:
                    logging.warning(f"[SYNC] No data or attachment found for {filename}")
                    continue

                decoded = base64.urlsafe_b64decode(data.encode('utf-8'))
                pdf_path = os.path.join('uploads', f"{email.replace('@', '_')}.pdf")
                with open(pdf_path, 'wb') as f:
                    f.write(decoded)
                logging.info(f"[SYNC] PDF saved to {pdf_path}")

                # Parse and sync events
                shifts = parse_schedule(pdf_path)
                for date_str, start, end in shifts:
                    event = {
                        'summary': 'Chuck E. Cheese Shift',
                        'start': {
                            'dateTime': f"{date_str}T{start}:00",
                            'timeZone': 'America/Los_Angeles'
                        },
                        'end': {
                            'dateTime': f"{date_str}T{end}:00",
                            'timeZone': 'America/Los_Angeles'
                        }
                    }
                    calendar.events().insert(calendarId='primary', body=event).execute()
                    logging.info(f"[SYNC] Event added: {date_str} {start}-{end}")
                return True

        logging.warning(f"[SYNC] No usable PDF found for {email}")
        return False

    except Exception as e:
        logging.exception(f"[SYNC ERROR] {email}: {e}")
        return False
    
@app.route('/run_sql', methods=['POST'])
def run_sql():
    if not session.get('is_admin'):
        flash("Unauthorized", "danger")
        return redirect(url_for('admin'))

    sql = request.form.get('command')
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall() if sql.strip().lower().startswith("select") else []
        conn.commit()

        if result:
            # Format results into readable string
            formatted = "\n".join(str(dict(row)) for row in result)
            logging.info(f"[SQL] {sql} => {formatted}")
        else:
            logging.info(f"[SQL] success")
    except Exception as e:
        logging.exception(f"[SQL ERROR] {e}")

    return redirect(url_for('admin'))