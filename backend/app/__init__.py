from flask import Flask
from flask_cors import CORS
from config.settings import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Do not connect to MySQL, create tables, or seed data during startup.
    # Vercel runs Flask as a serverless function and startup must be lightweight.
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        db.init_app(app)

    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
