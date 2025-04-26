from flask import Flask
from config import Config
import mysql.connector
from flask_login import LoginManager
import os
from datetime import datetime

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize login manager with app
    login_manager.init_app(app)

    # Initialize database
    from app.utils.db import init_app
    init_app(app)

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.auth.routes import auth
    from app.community.routes import community
    from app.complaints.routes import complaints
    from app.events.routes import events
    from app.notices.routes import notices
    from app.payments.routes import payments
    from app.voting.routes import voting

    app.register_blueprint(auth)
    app.register_blueprint(community)
    app.register_blueprint(complaints)
    app.register_blueprint(events)
    app.register_blueprint(notices)
    app.register_blueprint(payments)
    app.register_blueprint(voting)

    # Register context processors
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.now()

        return dict(now=now)

    return app
