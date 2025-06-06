# main.py
from flask import Flask
from template_generator import generate_templates
from app import app

# Register routes from separate modules
from routes.auth_routes import *
from routes.user_routes import *
from routes.admin_routes import *
from utils.sync_worker import background_sync_users

credentials_path = "credentials.json"
if not os.path.exists(credentials_path):
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        with open(credentials_path, "w") as f:
            f.write(creds_json)
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=[
            logging.FileHandler("server.log"),
            logging.StreamHandler()
        ]
    )
    @app.route('/')
    def index():
        return render_template('index.html')
    
    generate_templates()
    background_sync_users()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
