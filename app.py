import os
from flask import Flask
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from models import db  # import SQLAlchemy instance

def create_app():
    app = Flask(__name__)
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    print("OAUTHLIB_INSECURE_TRANSPORT =", os.getenv('OAUTHLIB_INSECURE_TRANSPORT'))
    app.config.from_object('config.Config')

    # Initialize database
    db.init_app(app)

    # Register routes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # Create tables automatically on startup
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
