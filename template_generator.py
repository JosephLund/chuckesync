# template_generator.py
import os
import time

next_sync_epoch = time.time() + 1800

def generate_templates():
    os.makedirs('templates', exist_ok=True)
    TEMPLATES = ['index.html', 'success.html', 'admin.html', 'privacy.html']
    for tmpl in TEMPLATES:
        try:
            os.remove(os.path.join('templates', tmpl))
        except FileNotFoundError:
            pass
    with open('templates/index.html', 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Chuck E Sync</title>
  <link rel='icon' type='image/png' href='{{ url_for('static', filename='images/logo.png') }}'>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap' rel='stylesheet'>
  <style>
    body {
      font-family: 'Open Sans', sans-serif;
      margin: 0;
      background: #fff3f8;
      color: #333;
    }
    header {
      background-color: #ec1c24;
      color: white;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo-text {
      font-size: 1.5rem;
      font-weight: 700;
    }
    .btn-primary {
      background-color: #ec1c24;
      border-color: #ec1c24;
    }
    .hero {
      background: linear-gradient(to bottom right, #6c2d91, #8d3dbf);
      color: white;
      padding: 4rem 2rem;
      text-align: center;
    }
    .hero img {
      height: 80px;
      margin-bottom: 1rem;
    }
    .hero h1 {
      font-size: 2.8rem;
      font-weight: 700;
    }
    .hero p {
      font-size: 1.25rem;
    }
    .main-actions {
      padding: 3rem 1rem;
      text-align: center;
    }
    .main-actions .btn {
      margin: 0.5rem;
      font-size: 1.1rem;
      padding: 0.75rem 1.5rem;
      border-radius: 8px;
    }
    .cookie-banner {
      position: fixed;
      bottom: 0;
      width: 100%;
      background-color: #fff0f0;
      border-top: 1px solid #ccc;
      padding: 1rem;
      text-align: center;
      z-index: 1000;
    }
  </style>
</head>
<body>
  <header>
    <div class='d-flex align-items-center'>
      <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Chuck E Sync Logo" style="height: 32px; margin-right: 10px;">
      <span class='logo-text'>Chuck E Sync</span>
    </div>
    {% if session.get('user_email') %}
    <form method="post" action="/logout">
      <button class="btn btn-outline-light">Logout</button>
    </form>
    {% endif %}
  </header>

  <section class="hero">
    <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
    <h1>Give us your shifts, and we’ll give you your schedule.</h1>
    <p>Automatically sync your Chuck E. Cheese shifts to Google Calendar.</p>
  </section>

  <section class="main-actions">
    <a class='btn btn-primary' href='/login'>Login with Google</a>
    {% if session.get('is_admin') %}
    <a class='btn btn-outline-dark' href='/admin'>Go to Admin Panel</a>
    {% endif %}
  </section>

  {% if not session.get('cookie_consent') %}
  <div class="cookie-banner">
    <form method="post" action="/accept_cookies">
      <p>This site uses cookies to keep you logged in. Do you accept?</p>
      <button class="btn btn-success">Accept Cookies</button>
    </form>
  </div>
  {% endif %}
</body>
</html>""")
    with open('templates/success.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Success - Chuck E Sync</title>
  <link rel='icon' type='image/png' href='{{ url_for('static', filename='images/logo.png') }}'>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap' rel='stylesheet'>
  <style>
    body {
      font-family: 'Open Sans', sans-serif;
      background: #fff3f8;
      margin: 0;
    }
    header {
      background-color: #ec1c24;
      color: white;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo-text {
      font-size: 1.5rem;
      font-weight: 700;
    }
    .hero {
      background: linear-gradient(to bottom right, #6c2d91, #8d3dbf);
      color: white;
      text-align: center;
      padding: 4rem 2rem;
    }
    .hero h1 {
      font-size: 2.5rem;
      margin-bottom: 1rem;
    }
    .main-content {
      text-align: center;
      padding: 3rem 2rem;
    }
    .button-group {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .button-group form,
    .button-group a {
      display: inline-block;
    }
    .button-group .btn {
      padding: 0.75rem 1.5rem;
      font-size: 1rem;
      border-radius: 8px;
    }
  </style>
</head>
<body>
  <header>
    <div class='d-flex align-items-center'>
      <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Chuck E Sync Logo" style="height: 32px; margin-right: 10px;">
      <span class='logo-text'>Chuck E Sync</span>
    </div>
    <form method="post" action="/logout">
      <button class="btn btn-outline-light">Logout</button>
    </form>
  </header>

  <section class="hero">
    <h1>You're all set!</h1>
    <p>Your shifts will now sync automatically with Google Calendar.</p>
  </section>

  <section class="main-content">
    <div class="button-group">  
      <form method="post" action="/clear_user/{{ session.get('user_email') }}" onsubmit="return confirm('Are you sure you want to remove yourself from Chuck E Sync?');">
        <button class="btn btn-danger">Remove Me from Sync</button>
      </form>
        {% if session.get('is_admin') %}
        <a class='btn btn-outline-dark' href='/admin'>Go to Admin Panel</a>
        {% endif %}
    </div>
  </section>
</body>
</html>""")
    with open('templates/privacy.html', 'w', encoding='utf-8') as f:
         f.write("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Chuck E Sync - Privacy Policy</title>
  <link rel="icon" type="image/png" href="/static/logo.png" />
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
  <style>
    body {
      background-color: #f8f9fa;
      font-family: 'Segoe UI', sans-serif;
    }
    header {
      background-color: #6c2d91;
      color: white;
      padding: 1.5rem;
      text-align: center;
    }
    .content {
      max-width: 800px;
      margin: 2rem auto;
      background: white;
      border-radius: 8px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
      padding: 2rem;
    }
    h1, h2 {
      color: #6c2d91;
    }
    a {
      color: #6c2d91;
      text-decoration: underline;
    }
    hr {
      margin-top: 3rem;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>

  <header>
    <h1>Chuck E Sync Privacy Policy</h1>
    <p class="lead mb-0">Protecting your data is our top priority.</p>
  </header>

  <main class="content">
    <p><strong>Effective Date:</strong> May 16, 2025</p>
    <p><strong>Website:</strong> <a href="https://chuckesync.com">https://chuckesync.com</a></p>

    <h2>1. Overview</h2>
    <p>
      Chuck E Sync helps Chuck E. Cheese employees automatically sync their weekly work schedules
      from email to Google Calendar. We value your privacy and only access the minimum data
      required to provide this service.
    </p>

    <h2>2. Information We Collect</h2>
    <ul>
      <li>Your Gmail inbox (only to find schedule emails from <code>nbo-noreply@alohaenterprise.com</code>)</li>
      <li>Your Google Calendar (to create work shift events)</li>
      <li>Your basic profile info (email address only)</li>
    </ul>

    <h2>3. How We Use Your Information</h2>
    <ul>
      <li>Detect your schedule email and download the PDF</li>
      <li>Parse shift details from that PDF</li>
      <li>Create events on your calendar</li>
    </ul>

    <h2>4. Data Storage and Security</h2>
    <ul>
      <li>Access tokens are securely stored and encrypted</li>
      <li>No email content or attachments are stored on our server</li>
      <li>Your calendar data is never saved or analyzed</li>
    </ul>

    <h2>5. User Control</h2>
    <p>You can revoke Chuck E Sync’s access anytime by visiting:
      <a href="https://myaccount.google.com/permissions" target="_blank">https://myaccount.google.com/permissions</a>
    </p>
    <p>You may also opt out directly via the app dashboard.</p>

    <h2>6. Third-Party Services</h2>
    <ul>
      <li>Google OAuth 2.0 for authentication</li>
      <li>Render.com for hosting</li>
    </ul>

    <h2>7. Contact</h2>
    <p>
      <strong>Joseph Lund</strong><br />
      Email: <a href="mailto:josephtlund@gmail.com">josephtlund@gmail.com</a><br />
      Website: <a href="https://chuckesync.com">https://chuckesync.com</a>
    </p>

    <hr />
    <p class="text-muted small">Chuck E Sync is not affiliated with or endorsed by Chuck E. Cheese or CEC Entertainment, Inc.</p>
  </main>

</body>
</html>
""")

    with open('templates/admin.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Admin - Chuck E Sync</title>
  <link rel='icon' type='image/png' href='{{ url_for('static', filename='images/logo.png') }}'>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'>
  <link href='https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap' rel='stylesheet'>
  <style>
    body {
      font-family: 'Open Sans', sans-serif;
      background: #fff3f8;
      margin: 0;
      padding-bottom: 120px;
    }
    header {
      background-color: #ec1c24;
      color: white;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo-text {
      font-size: 1.5rem;
      font-weight: 700;
    }
    .admin-panel {
      padding: 3rem 2rem;
    }
    .admin-panel h1 {
      color: #6c2d91;
      font-weight: bold;
      margin-bottom: 2rem;
    }
    .user-entry {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
    .user-email {
      font-weight: 600;
    }
    .user-actions form,
    .user-actions a {
      display: inline-block;
      margin-left: 0.5rem;
    }
    .user-actions .btn {
      font-size: 0.9rem;
    }
    .log-container {
      position: fixed;
      bottom: 3.5rem;
      left: 0;
      width: 100%;
      background-color: #000;
      color: #fff;
      font-family: monospace;
      border-top: 1px solid #333;
      max-height: 300px;
      overflow-y: auto;
      padding: 1rem;
      white-space: pre-wrap;
      z-index: 1040;
    }
    .log-container .log-info {
      color: #0f0;
    }
    .log-container .log-warning {
      color: #ff0;
    }
    .log-container .log-error {
      color: #f00;
    }
    .command-bar {
      position: fixed;
      bottom: 0;
      left: 0;
      width: 100%;
      background-color: #111;
      padding: 0.75rem;
      display: flex;
      gap: 0.5rem;
      border-top: 1px solid #333;
      z-index: 1050;
    }
    .command-bar input {
      flex: 1;
      padding: 0.5rem;
      font-family: monospace;
      font-size: 1rem;
      background-color: #222;
      color: #0f0;
      border: 1px solid #444;
    }
  </style>
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      const cmdInput = document.querySelector(".command-bar input[name='command']");
      const logContainer = document.querySelector(".log-container");

      if (cmdInput) {
        cmdInput.focus();
        cmdInput.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            cmdInput.closest('form').submit();
          }
        });
      }

      if (logContainer) {
        logContainer.scrollTop = logContainer.scrollHeight;
      }
    });
  const syncEpoch = {{ next_sync_epoch }};
  function updateTimer() {
    const now = Math.floor(Date.now() / 1000);
    const remaining = Math.max(syncEpoch - now, 0);
    const minutes = Math.floor(remaining / 60);
    const seconds = remaining % 60;
    document.getElementById('sync-timer').textContent = `${minutes}m ${seconds}s`;
  }
  setInterval(updateTimer, 1000);
  updateTimer();
  </script>
</head>
<body>
  <header>
    <div class='d-flex align-items-center'>
      <img src="{{ url_for('static', filename='images/logo.png') }}" alt="Chuck E Sync Logo" style="height: 32px; margin-right: 10px;">
      <span class='logo-text'>Chuck E Sync</span>
    </div>
    <form method="post" action="/logout">
      <button class="btn btn-outline-light">Logout</button>
    </form>
  </header>


  <div class="admin-panel container">
    <h1>Admin Panel</h1>
    {% for user in users %}
    <div class="user-entry">
      <div class="user-email">{{ user['email'] }} {% if user['is_admin'] %}<span class="badge bg-warning text-dark">Admin</span>{% endif %}</div>
      <div class="user-actions">
        <form method="post" action="/test_user/{{ user['email'] }}">
          <button class="btn btn-outline-primary btn-sm" onclick="return confirm('Test sync for {{ user['email'] }}?')">Test Sync</button>
        </form>
        <form method="post" action="/clear_user/{{ user['email'] }}">
          <button class="btn btn-outline-danger btn-sm" onclick="return confirm('Delete {{ user['email'] }} from the system?')">Delete</button>
        </form>
        <form method="post" action="/toggle_admin/{{ user['email'] }}">
          <button class="btn btn-outline-warning btn-sm">Toggle Admin</button>
        </form>
        <form method="post" action="/sync_user_calendar/{{ user['email'] }}">
          <button class="btn btn-outline-warning btn-sm">Sync</button>
        </form>
                
      </div>
    </div>
    {% endfor %}
    <a href="/" class="btn btn-secondary mt-4">Back to Home</a>
</div>
  </div>
<div class="mt-3">
  <strong>Next sync in:</strong> <span id="sync-timer">Loading...</span>
</div>

  <div class="log-container">
    <strong>Server Logs:</strong>
    <pre>{{ logs|safe }}</pre>
  </div>

    <!-- Python + SQL Command Bar -->
    <form class="command-bar" method="post">
      <input name="command" type="text" placeholder="Enter a Python or SQL command..." required>
      <button type="submit" class="btn btn-success" formaction="/exec_command">Run Python</button>
      <button type="submit" class="btn btn-warning" formaction="/run_sql">Run SQL</button>
    </form>
</body>
</html>""")
