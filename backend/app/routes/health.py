from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@health_bp.get("/health/db")
def database_health():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "database": "connected"})
    except SQLAlchemyError as exc:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }), 503
