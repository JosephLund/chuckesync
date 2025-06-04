# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return "Hello from Chuck E Sync v2!"

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask
from config import Config

# Blueprint imports will come next as we build routes
# from routes.auth_routes import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    # app.register_blueprint(auth_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
