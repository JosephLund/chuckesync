import os
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from flask import Flask, logging
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.shifts_routes import shifts_bp
from models import db 
from datetime import datetime

def create_app():
    app = Flask(__name__)
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)

    # Register routes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(shifts_bp)

    
    @app.template_filter("logtime")
    def format_log_time(value, tz_str="America/Los_Angeles"):
        try:
            dt = datetime.fromisoformat(value)
            try:
                tz = ZoneInfo(tz_str or "America/Los_Angeles")
            except (ZoneInfoNotFoundError, ValueError):
                tz = ZoneInfo("America/Los_Angeles")
            local_dt = dt.astimezone(tz)
            return local_dt.strftime("%b %d %I:%M:%S %p")
        except Exception as e:
            return value

    # Create tables automatically on startup
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        handlers=[
            logging.FileHandler("server.log"),
            logging.StreamHandler()
        ]
    )
    app = create_app()
    app.run(debug=True)