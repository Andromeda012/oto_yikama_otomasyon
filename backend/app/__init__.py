from flask import Flask
from flask_cors import CORS

from config.settings import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # The database is initialized only when an external DATABASE_URL is supplied.
    # No connection, schema creation, or seed data is performed during startup.
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        db.init_app(app)

    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
