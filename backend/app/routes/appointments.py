from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Appointment, AppointmentService, Customer, Service, Vehicle

appointments_bp = Blueprint("appointments_api", __name__, url_prefix="/api/appointments")

STATUSES = {"scheduled", "arrived", "in_service", "completed", "cancelled"}
ACTIVE_STATUSES = {"scheduled", "arrived", "in_service"}


def parse_dt(value):
    if not value:
        raise ValueError("Randevu başlangıç zamanı zorunludur.")
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed.replace(tzinfo=None)


def serialize(a):
    services = sorted(a.services, key=lambda item: item.service.name.lower())
    total_price = sum((float(x.price) for x in services), 0.0)
    total_duration = sum((x.duration_minutes for x in services), 0)
    return {
        "id": a.id,
        "customer": {
            "id": a.customer.id,
            "name": f"{a.customer.first_name} {a.customer.last_name}",
            "phone": a.customer.phone,
        },
        "vehicle": {
            "id": a.vehicle.id,
            "plate": a.vehicle.plate,
            "brand": a.vehicle.brand or "",
            "model": a.vehicle.model or "",
        },
        "start_at": a.start_at.isoformat(),
        "end_at": a.end_at.isoformat(),
        "status": a.status,
        "notes": a.notes or "",
        "services": [
            {
                "id": x.service.id,
                "name": x.service.name,
                "price": float(x.price),
                "duration_minutes": x.duration_minutes,
            }
            for x in services
        ],
        "total_price": total_price,
        "total_duration_minutes": total_duration,
    }


def get_service_ids(data, appointment=None):
    raw = data.get("service_ids")
    if raw is None and appointment is not None:
        raw = [item.service_id for item in appointment.services]
    if not isinstance(raw, list):
        raise ValueError("service_ids bir liste olmalıdır.")
    ids = []
    for value in raw:
        service_id = int(value)
        if service_id not in ids:
            ids.append(service_id)
    if not ids:
        raise ValueError("En az bir hizmet seçilmelidir.")
    return ids


def find_conflict(start_at, end_at, exclude_id=None):
    query = Appointment.query.filter(
        Appointment.status.in_(ACTIVE_STATUSES),
        Appointment.start_at < end_at,
        Appointment.end_at > start_at,
    )
    if exclude_id is not None:
        query = query.filter(Appointment.id != exclude_id)
    return query.order_by(Appointment.start_at.asc()).first()


def validate_entities(data, service_ids):
    customer = db.session.get(Customer, data.get("customer_id"))
    vehicle = db.session.get(Vehicle, data.get("vehicle_id"))
    if not customer:
        raise ValueError("Müşteri bulunamadı.")
    if not vehicle or vehicle.customer_id != customer.id:
        raise ValueError("Seçilen araç bu müşteriye ait değil.")

    services = Service.query.filter(
        Service.id.in_(service_ids), Service.is_active.is_(True)
    ).all()
    service_map = {service.id: service for service in services}
    if len(service_map) != len(service_ids):
        raise ValueError("Seçilen hizmetlerden biri geçersiz veya pasif.")
    return customer, vehicle, [service_map[item] for item in service_ids]


def apply_services(appointment, services):
    appointment.services.clear()
    db.session.flush()
    for service in services:
        db.session.add(
            AppointmentService(
                appointment_id=appointment.id,
                service_id=service.id,
                price=service.price,
                duration_minutes=service.duration_minutes,
            )
        )


@appointments_bp.get("")
def list_appointments():
    date = request.args.get("date")
    status = request.args.get("status")
    query = Appointment.query.order_by(Appointment.start_at.asc())

    if date:
        try:
            day = datetime.fromisoformat(date)
        except ValueError:
            return jsonify({"error": "Geçersiz tarih."}), 400
        query = query.filter(
            Appointment.start_at >= day,
            Appointment.start_at < day + timedelta(days=1),
        )
    if status and status in STATUSES:
        query = query.filter(Appointment.status == status)

    return jsonify([serialize(item) for item in query.all()])


@appointments_bp.get("/lookups")
def lookups():
    customers = Customer.query.order_by(Customer.first_name, Customer.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.plate).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    return jsonify({
        "customers": [
            {"id": c.id, "name": f"{c.first_name} {c.last_name}", "phone": c.phone}
            for c in customers
        ],
        "vehicles": [
            {
                "id": v.id,
                "customer_id": v.customer_id,
                "plate": v.plate,
                "brand": v.brand or "",
                "model": v.model or "",
            }
            for v in vehicles
        ],
        "services": [
            {
                "id": s.id,
                "name": s.name,
                "price": float(s.price),
                "duration_minutes": s.duration_minutes,
            }
            for s in services
        ],
    })


@appointments_bp.post("")
def create_appointment():
    data = request.get_json() or {}
    try:
        start_at = parse_dt(data.get("start_at"))
        service_ids = get_service_ids(data)
        customer, vehicle, services = validate_entities(data, service_ids)
        duration = sum(service.duration_minutes for service in services)
        end_at = start_at + timedelta(minutes=duration)
        status = data.get("status", "scheduled")
        if status not in STATUSES:
            raise ValueError("Geçersiz randevu durumu.")
        if status in ACTIVE_STATUSES:
            conflict = find_conflict(start_at, end_at)
            if conflict:
                return jsonify({
                    "error": "Bu saat aralığında başka bir randevu bulunuyor.",
                    "conflict": serialize(conflict),
                }), 409

        appointment = Appointment(
            customer_id=customer.id,
            vehicle_id=vehicle.id,
            start_at=start_at,
            end_at=end_at,
            status=status,
            notes=(data.get("notes") or "").strip() or None,
        )
        db.session.add(appointment)
        db.session.flush()
        apply_services(appointment, services)
        db.session.commit()
        return jsonify(serialize(appointment)), 201
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Geçersiz randevu bilgileri."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Randevu kaydedilirken veritabanı hatası oluştu."}), 500


@appointments_bp.put("/<int:appointment_id>")
def update_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Randevu bulunamadı."}), 404

    data = request.get_json() or {}
    try:
        service_ids = get_service_ids(data, appointment)
        entity_data = {
            "customer_id": data.get("customer_id", appointment.customer_id),
            "vehicle_id": data.get("vehicle_id", appointment.vehicle_id),
        }
        customer, vehicle, services = validate_entities(entity_data, service_ids)
        start_at = parse_dt(data["start_at"]) if data.get("start_at") else appointment.start_at
        end_at = start_at + timedelta(minutes=sum(s.duration_minutes for s in services))
        status = data.get("status", appointment.status)
        if status not in STATUSES:
            raise ValueError("Geçersiz randevu durumu.")
        if status in ACTIVE_STATUSES:
            conflict = find_conflict(start_at, end_at, exclude_id=appointment.id)
            if conflict:
                return jsonify({
                    "error": "Bu saat aralığında başka bir randevu bulunuyor.",
                    "conflict": serialize(conflict),
                }), 409

        appointment.customer_id = customer.id
        appointment.vehicle_id = vehicle.id
        appointment.start_at = start_at
        appointment.end_at = end_at
        appointment.status = status
        appointment.notes = (data.get("notes", appointment.notes or "") or "").strip() or None
        apply_services(appointment, services)
        db.session.commit()
        return jsonify(serialize(appointment))
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Geçersiz randevu bilgileri."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Randevu güncellenirken veritabanı hatası oluştu."}), 500


@appointments_bp.patch("/<int:appointment_id>/status")
def update_status(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Randevu bulunamadı."}), 404
    data = request.get_json() or {}
    status = data.get("status")
    if status not in STATUSES:
        return jsonify({"error": "Geçersiz randevu durumu."}), 400
    appointment.status = status
    db.session.commit()
    return jsonify(serialize(appointment))


@appointments_bp.delete("/<int:appointment_id>")
def cancel_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Randevu bulunamadı."}), 404
    appointment.status = "cancelled"
    db.session.commit()
    return jsonify({"success": True, "appointment": serialize(appointment)})
