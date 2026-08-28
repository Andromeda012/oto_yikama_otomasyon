from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@health_bp.get("/health/db")
def database_health():
    """Check whether Flask can reach the configured MySQL database."""
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({
            "status": "ok",
            "database": "connected",
        }), 200
    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "database": "disconnected",
        }), 503
