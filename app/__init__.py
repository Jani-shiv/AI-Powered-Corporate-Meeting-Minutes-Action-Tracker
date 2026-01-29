from flask import Flask
from config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    db.init_app(app)

    # Register Blueprints
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    # Create Tables
    with app.app_context():
        db.create_all()

    return app
