from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

from config.settings import Config
from app.extensions import db


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


def create_app(config_class=Config):
    # In Vercel, the Vue build is bundled with the Flask function and served
    # by Flask. This keeps the SPA and API in one deployment.
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Never connect to MySQL, create tables, or seed data during startup.
    # Database access happens only when an API endpoint actually needs it.
    if app.config.get("SQLALCHEMY_DATABASE_URI"):
        db.init_app(app)

    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    from app.routes import register_blueprints
    register_blueprints(app)

    @app.get("/")
    def frontend_root():
        return send_from_directory(FRONTEND_DIST, "index.html")

    @app.get("/<path:path>")
    def frontend_routes(path):
        # API routes are handled by their blueprints above.
        # Existing frontend assets are served directly; all other paths
        # fall back to index.html so Vue Router can handle SPA navigation.
        requested = FRONTEND_DIST / path
        if requested.is_file():
            return send_from_directory(FRONTEND_DIST, path)
        return send_from_directory(FRONTEND_DIST, "index.html")

    return app
