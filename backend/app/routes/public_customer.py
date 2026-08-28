import json
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Appointment, AppointmentService, Customer, Service, Vehicle, SystemSettings

public_customer_bp = Blueprint("public_customer_api", __name__, url_prefix="/api/public")

DEFAULT_HOURS = {
    "monday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "tuesday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "wednesday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "thursday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "friday": {"enabled": True, "open": "08:00", "close": "19:00"},
    "saturday": {"enabled": True, "open": "09:00", "close": "18:00"},
    "sunday": {"enabled": False, "open": "09:00", "close": "17:00"},
}
DAY_KEYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
ACTIVE_STATUSES = {"scheduled", "arrived", "in_service"}


def settings():
    item = SystemSettings.query.first()
    if not item:
        return 30, DEFAULT_HOURS, 30
    try:
        hours = json.loads(item.business_hours or "{}")
    except (TypeError, ValueError):
        hours = DEFAULT_HOURS
    return int(item.appointment_slot_minutes or 30), hours or DEFAULT_HOURS, int(item.appointment_advance_days or 30)


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError("Geçersiz tarih.")


def parse_slot(value):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError):
        raise ValueError("Geçersiz tarih veya saat.")


def normalize_phone(value):
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def normalize_plate(value):
    return " ".join(str(value or "").upper().strip().split())


def service_json(service):
    return {
        "id": service.id,
        "name": service.name,
        "price": float(service.price or 0),
        "duration_minutes": service.duration_minutes,
        "description": service.description or "",
    }


def appointment_json(item):
    service = item.services[0].service if item.services else None
    return {
        "id": item.id,
        "date": item.start_at.date().isoformat(),
        "time": item.start_at.strftime("%H:%M"),
        "start_at": item.start_at.isoformat(),
        "end_at": item.end_at.isoformat(),
        "status": item.status,
        "notes": item.notes or "",
        "customer": f"{item.customer.first_name} {item.customer.last_name}",
        "phone": item.customer.phone,
        "plate": item.vehicle.plate,
        "service": service_json(service) if service else None,
    }


def find_identity(phone, plate):
    phone = normalize_phone(phone)
    plate = normalize_plate(plate)
    if not phone or not plate:
        return None, None
    candidates = Customer.query.all()
    customer = next((c for c in candidates if normalize_phone(c.phone) == phone), None)
    vehicle = Vehicle.query.filter_by(plate=plate).first()
    if vehicle and customer and vehicle.customer_id != customer.id:
        return customer, None
    return customer, vehicle


def get_service(service_id):
    if not service_id:
        return None
    try:
        service = db.session.get(Service, int(service_id))
    except (TypeError, ValueError):
        service = None
    if not service or not service.is_active:
        raise ValueError("Seçilen hizmet bulunamadı.")
    return service


def validate_slot(start_at, duration_minutes=None, exclude_id=None):
    slot_minutes, hours, advance_days = settings()
    duration_minutes = int(duration_minutes or slot_minutes)
    today = datetime.now().date()
    if start_at.date() < today:
        raise ValueError("Geçmiş bir tarih seçilemez.")
    if (start_at.date() - today).days > advance_days:
        raise ValueError(f"En fazla {advance_days} gün sonrasına randevu alınabilir.")

    day_cfg = hours.get(DAY_KEYS[start_at.weekday()], {})
    if not day_cfg.get("enabled", False):
        raise ValueError("İşletme bu gün kapalı.")
    try:
        opening = datetime.combine(start_at.date(), datetime.strptime(day_cfg["open"], "%H:%M").time())
        closing = datetime.combine(start_at.date(), datetime.strptime(day_cfg["close"], "%H:%M").time())
    except (KeyError, ValueError):
        raise ValueError("Çalışma saatleri geçersiz.")

    end_at = start_at + timedelta(minutes=duration_minutes)
    if start_at < opening or end_at > closing:
        raise ValueError("Seçilen saat işletmenin çalışma saatleri dışında.")
    if start_at <= datetime.now():
        raise ValueError("Geçmiş bir saat seçilemez.")

    query = Appointment.query.filter(
        Appointment.status.in_(ACTIVE_STATUSES),
        Appointment.start_at < end_at,
        Appointment.end_at > start_at,
    )
    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)
    if query.first():
        raise ValueError("Bu saat dolu. Lütfen başka bir saat seçin.")
    return end_at


@public_customer_bp.get("/company")
def public_company():
    from app.models import CompanyProfile
    profile = CompanyProfile.query.first()
    return jsonify({"company_name": (profile.company_name if profile else "Oto Yıkama"), "logo_url": ""})


@public_customer_bp.get("/services")
def public_services():
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    return jsonify({"services": [service_json(x) for x in services]})


@public_customer_bp.get("/availability")
def availability():
    try:
        day = parse_date(request.args.get("date"))
        base_slot_minutes, hours, _ = settings()
        service = get_service(request.args.get("service_id")) if request.args.get("service_id") else None
        duration = service.duration_minutes if service else base_slot_minutes
        cfg = hours.get(DAY_KEYS[day.weekday()], {})
        if not cfg.get("enabled", False):
            return jsonify({"date": day.isoformat(), "slots": [], "closed": True})
        opening = datetime.combine(day, datetime.strptime(cfg["open"], "%H:%M").time())
        closing = datetime.combine(day, datetime.strptime(cfg["close"], "%H:%M").time())
        busy = Appointment.query.filter(
            Appointment.status.in_(ACTIVE_STATUSES),
            Appointment.start_at < closing,
            Appointment.end_at > opening,
        ).all()
        slots = []
        cursor = opening
        now = datetime.now()
        while cursor + timedelta(minutes=duration) <= closing:
            end = cursor + timedelta(minutes=duration)
            is_busy = any(a.start_at < end and a.end_at > cursor for a in busy)
            slots.append({"time": cursor.strftime("%H:%M"), "available": not is_busy and cursor > now})
            cursor += timedelta(minutes=base_slot_minutes)
        return jsonify({"date": day.isoformat(), "slots": slots, "closed": False, "slot_minutes": base_slot_minutes, "duration_minutes": duration})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except SQLAlchemyError:
        return jsonify({"error": "Müsaitlik bilgileri alınırken veritabanı hatası oluştu."}), 500


@public_customer_bp.get("/account")
def get_public_account():
    phone = normalize_phone(request.args.get("phone"))
    if not phone:
        return jsonify({"account": None, "vehicles": []})
    customer = next((c for c in Customer.query.all() if normalize_phone(c.phone) == phone), None)
    if not customer:
        return jsonify({"account": None, "vehicles": []})
    return jsonify({
        "account": {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "phone": customer.phone,
            "email": customer.email or "",
            "notes": customer.notes or "",
        },
        "vehicles": [
            {"id": v.id, "plate": v.plate, "brand": v.brand or "", "model": v.model or "", "year": v.year, "color": v.color or "", "notes": v.notes or ""}
            for v in customer.vehicles
        ],
    })


@public_customer_bp.post("/account")
def save_public_account():
    data = request.get_json(silent=True) or {}
    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    plate = normalize_plate(data.get("plate"))
    if not first_name or not last_name or not normalize_phone(phone) or not plate:
        return jsonify({"error": "Ad, soyad, telefon ve plaka zorunludur."}), 400

    try:
        normalized = normalize_phone(phone)
        customer = next((c for c in Customer.query.all() if normalize_phone(c.phone) == normalized), None)
        if not customer:
            customer = Customer(first_name=first_name, last_name=last_name, phone=phone)
            db.session.add(customer)
            db.session.flush()
        else:
            customer.first_name = first_name
            customer.last_name = last_name
            customer.phone = phone
        customer.email = str(data.get("email", "")).strip() or None
        customer.notes = str(data.get("notes", "")).strip() or None

        vehicle = Vehicle.query.filter_by(plate=plate).first()
        if vehicle and vehicle.customer_id != customer.id:
            raise ValueError("Bu plaka başka bir cari kaydına ait.")
        if not vehicle:
            vehicle = Vehicle(customer_id=customer.id, plate=plate)
            db.session.add(vehicle)
        vehicle.brand = str(data.get("brand", "")).strip() or None
        vehicle.model = str(data.get("model", "")).strip() or None
        vehicle.year = data.get("year") or None
        vehicle.color = str(data.get("color", "")).strip() or None
        vehicle.notes = str(data.get("vehicle_notes", "")).strip() or None
        db.session.commit()
        return jsonify({
            "account": {"id": customer.id, "first_name": customer.first_name, "last_name": customer.last_name, "phone": customer.phone, "email": customer.email or "", "notes": customer.notes or ""},
            "vehicle": {"id": vehicle.id, "plate": vehicle.plate, "brand": vehicle.brand or "", "model": vehicle.model or "", "year": vehicle.year, "color": vehicle.color or "", "notes": vehicle.notes or ""},
        }), 200
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 409
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Bu bilgilerle hesap kaydedilemedi. Plaka zaten başka bir kayda ait olabilir."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Hesap kaydedilirken veritabanı hatası oluştu."}), 500


@public_customer_bp.get("/appointments")
def public_appointments():
    phone = normalize_phone(request.args.get("phone"))
    plate = normalize_plate(request.args.get("plate"))
    if not phone or not plate:
        return jsonify({"error": "Telefon ve plaka zorunludur."}), 400
    customer, vehicle = find_identity(phone, plate)
    if not customer or not vehicle or vehicle.customer_id != customer.id:
        return jsonify({"appointments": []})
    items = Appointment.query.filter(
        Appointment.customer_id == customer.id,
        Appointment.vehicle_id == vehicle.id,
        Appointment.status != "cancelled",
    ).order_by(Appointment.start_at.desc()).limit(20).all()
    return jsonify({"appointments": [appointment_json(x) for x in items]})


@public_customer_bp.post("/appointments")
def create_public_appointment():
    data = request.get_json(silent=True) or {}
    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    plate = normalize_plate(data.get("plate"))
    if not first_name or not last_name or not phone or not plate:
        return jsonify({"error": "Ad, soyad, telefon ve plaka zorunludur."}), 400
    try:
        service = get_service(data.get("service_id"))
        if not service:
            raise ValueError("Randevu için bir hizmet seçmelisiniz.")
        start_at = parse_slot(data.get("start_at"))
        end_at = validate_slot(start_at, service.duration_minutes)
        customer, vehicle = find_identity(phone, plate)
        if vehicle and customer and vehicle.customer_id != customer.id:
            raise ValueError("Bu plaka başka bir cari kaydına ait.")
        if not customer:
            customer = Customer(first_name=first_name, last_name=last_name, phone=phone)
            db.session.add(customer)
            db.session.flush()
        else:
            customer.first_name = first_name
            customer.last_name = last_name
            customer.phone = phone
        if not vehicle:
            vehicle = Vehicle(customer_id=customer.id, plate=plate)
            db.session.add(vehicle)
            db.session.flush()
        appointment = Appointment(
            customer_id=customer.id,
            vehicle_id=vehicle.id,
            start_at=start_at,
            end_at=end_at,
            status="scheduled",
            notes="Online randevu",
        )
        db.session.add(appointment)
        db.session.flush()
        db.session.add(AppointmentService(appointment_id=appointment.id, service_id=service.id, price=service.price, duration_minutes=service.duration_minutes))
        db.session.commit()
        return jsonify(appointment_json(appointment)), 201
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Randevu kaydedilemedi. Plaka veya hizmet bilgilerini kontrol edin."}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Randevu kaydedilirken veritabanı hatası oluştu."}), 500


@public_customer_bp.put("/appointments/<int:appointment_id>")
def update_public_appointment(appointment_id):
    data = request.get_json(silent=True) or {}
    phone = normalize_phone(data.get("phone"))
    plate = normalize_plate(data.get("plate"))
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment or appointment.status == "cancelled":
        return jsonify({"error": "Randevu bulunamadı."}), 404
    if normalize_phone(appointment.customer.phone) != phone or normalize_plate(appointment.vehicle.plate) != plate:
        return jsonify({"error": "Randevu bilgileri doğrulanamadı."}), 403
    try:
        service = appointment.services[0].service if appointment.services else None
        if data.get("service_id"):
            service = get_service(data.get("service_id"))
        duration = service.duration_minutes if service else settings()[0]
        start_at = parse_slot(data.get("start_at"))
        end_at = validate_slot(start_at, duration, exclude_id=appointment.id)
        appointment.start_at = start_at
        appointment.end_at = end_at
        if service:
            existing = appointment.services[0] if appointment.services else None
            if existing:
                existing.service_id = service.id
                existing.price = service.price
                existing.duration_minutes = service.duration_minutes
            else:
                db.session.add(AppointmentService(appointment_id=appointment.id, service_id=service.id, price=service.price, duration_minutes=service.duration_minutes))
        db.session.commit()
        return jsonify(appointment_json(appointment))
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Randevu güncellenirken veritabanı hatası oluştu."}), 500
