from flask import Flask, jsonify, request, session
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

    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"), supports_credentials=True)

    @app.before_request
    def require_admin_for_api():
        # Authentication is intentionally limited to the management API.
        # Public customer pages do not require a login.
        if not request.path.startswith("/api/"):
            return None
        if request.method == "OPTIONS":
            return None
        if request.path.startswith("/api/auth/") or request.path.startswith("/api/public/") or request.path == "/api/health/db":
            return None
        if not session.get("is_admin"):
            return jsonify({"error": "Yönetici girişi gerekli."}), 401
        return None

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
