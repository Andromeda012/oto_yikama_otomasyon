import json
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import SystemSettings

settings_bp = Blueprint("settings_api", __name__, url_prefix="/api/settings")

DEFAULT_HOURS = {
    "monday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "tuesday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "wednesday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "thursday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "friday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "saturday": {"enabled": True, "open": "09:00", "close": "18:00"},
    "sunday": {"enabled": False, "open": "09:00", "close": "17:00"},
}

FIELDS = [
    "timezone", "currency", "appointment_slot_minutes", "appointment_advance_days",
    "appointment_allow_past", "appointment_auto_job", "reminder_enabled",
    "reminder_hours_before", "sms_enabled", "sms_provider", "sms_sender",
    "whatsapp_enabled", "whatsapp_provider", "whatsapp_phone", "business_hours"
]

def get_or_create():
    settings = SystemSettings.query.first()
    if settings is None:
        settings = SystemSettings(business_hours=json.dumps(DEFAULT_HOURS, ensure_ascii=False))
        db.session.add(settings)
        db.session.commit()
    return settings

def serialize(settings):
    data = {field: getattr(settings, field) for field in FIELDS if field != "business_hours"}
    try:
        data["business_hours"] = json.loads(settings.business_hours or "{}")
    except (TypeError, ValueError):
        data["business_hours"] = DEFAULT_HOURS
    data["id"] = settings.id
    return data

@settings_bp.get("")
def get_settings():
    return jsonify(serialize(get_or_create()))

@settings_bp.put("")
def update_settings():
    data = request.get_json(silent=True) or {}
    settings = get_or_create()
    integer_fields = {"appointment_slot_minutes": (5, 240), "appointment_advance_days": (0, 365), "reminder_hours_before": (1, 168)}
    for field, (minimum, maximum) in integer_fields.items():
        if field in data:
            try:
                value = int(data[field])
            except (TypeError, ValueError):
                return jsonify({"error": f"{field} geçerli bir sayı olmalıdır."}), 400
            if not minimum <= value <= maximum:
                return jsonify({"error": f"{field} geçerli aralıkta değil."}), 400
            setattr(settings, field, value)
    for field in ["appointment_allow_past", "appointment_auto_job", "reminder_enabled", "sms_enabled", "whatsapp_enabled"]:
        if field in data:
            setattr(settings, field, bool(data[field]))
    for field in ["timezone", "currency", "sms_provider", "sms_sender", "whatsapp_provider", "whatsapp_phone"]:
        if field in data:
            setattr(settings, field, str(data[field] or "").strip())
    if "business_hours" in data:
        hours = data["business_hours"]
        if not isinstance(hours, dict):
            return jsonify({"error": "Çalışma saatleri geçersiz."}), 400
        for day, value in hours.items():
            if not isinstance(value, dict) or not all(k in value for k in ("enabled", "open", "close")):
                return jsonify({"error": f"{day} çalışma saati geçersiz."}), 400
        settings.business_hours = json.dumps(hours, ensure_ascii=False)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Ayarlar kaydedilemedi."}), 500
    return jsonify(serialize(settings))
