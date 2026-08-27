from datetime import datetime, timedelta
from decimal import Decimal
from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Appointment, AppointmentService, Customer, Service, Vehicle

appointments_bp = Blueprint("appointments_api", __name__, url_prefix="/api/appointments")

STATUSES = {"scheduled", "arrived", "in_service", "completed", "cancelled"}


def parse_dt(value):
    if not value:
        raise ValueError("start_at is required")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def serialize(a):
    return {
        "id": a.id,
        "customer": {"id": a.customer.id, "name": f"{a.customer.first_name} {a.customer.last_name}", "phone": a.customer.phone},
        "vehicle": {"id": a.vehicle.id, "plate": a.vehicle.plate, "brand": a.vehicle.brand, "model": a.vehicle.model},
        "start_at": a.start_at.isoformat(),
        "end_at": a.end_at.isoformat(),
        "status": a.status,
        "notes": a.notes or "",
        "services": [{"id": x.service.id, "name": x.service.name, "price": float(x.price), "duration_minutes": x.duration_minutes} for x in a.services],
    }


def has_conflict(start_at, end_at, exclude_id=None):
    q = Appointment.query.filter(
        Appointment.status.notin_(["cancelled", "completed"]),
        Appointment.start_at < end_at,
        Appointment.end_at > start_at,
    )
    if exclude_id:
        q = q.filter(Appointment.id != exclude_id)
    return q.first() is not None


@appointments_bp.get("")
def list_appointments():
    date = request.args.get("date")
    query = Appointment.query.order_by(Appointment.start_at.asc())
    if date:
        day = datetime.fromisoformat(date)
        query = query.filter(Appointment.start_at >= day, Appointment.start_at < day + timedelta(days=1))
    return jsonify([serialize(a) for a in query.all()])


@appointments_bp.get("/lookups")
def lookups():
    customers = Customer.query.order_by(Customer.first_name, Customer.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.plate).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    return jsonify({
        "customers": [{"id": c.id, "name": f"{c.first_name} {c.last_name}", "phone": c.phone} for c in customers],
        "vehicles": [{"id": v.id, "customer_id": v.customer_id, "plate": v.plate, "brand": v.brand, "model": v.model} for v in vehicles],
        "services": [{"id": s.id, "name": s.name, "price": float(s.price), "duration_minutes": s.duration_minutes} for s in services],
    })


@appointments_bp.post("")
def create_appointment():
    data = request.get_json() or {}
    try:
        start_at = parse_dt(data.get("start_at"))
        service_ids = [int(x) for x in data.get("service_ids", [])]
        if not service_ids:
            return jsonify({"error": "At least one service is required"}), 400
        services = Service.query.filter(Service.id.in_(service_ids), Service.is_active.is_(True)).all()
        if len(services) != len(set(service_ids)):
            return jsonify({"error": "One or more services are invalid"}), 400
        customer = db.session.get(Customer, data.get("customer_id"))
        vehicle = db.session.get(Vehicle, data.get("vehicle_id"))
        if not customer or not vehicle or vehicle.customer_id != customer.id:
            return jsonify({"error": "Customer and vehicle do not match"}), 400
        duration = sum(s.duration_minutes for s in services)
        end_at = start_at + timedelta(minutes=duration)
        if has_conflict(start_at, end_at):
            return jsonify({"error": "Appointment time conflicts with another appointment"}), 409
        a = Appointment(customer_id=customer.id, vehicle_id=vehicle.id, start_at=start_at, end_at=end_at, status=data.get("status", "scheduled"), notes=data.get("notes"))
        if a.status not in STATUSES:
            return jsonify({"error": "Invalid status"}), 400
        db.session.add(a)
        db.session.flush()
        for service in services:
            db.session.add(AppointmentService(appointment_id=a.id, service_id=service.id, price=service.price, duration_minutes=service.duration_minutes))
        db.session.commit()
        return jsonify(serialize(a)), 201
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid appointment data"}), 400


@appointments_bp.put("/<int:appointment_id>")
def update_appointment(appointment_id):
    a = db.session.get(Appointment, appointment_id)
    if not a:
        return jsonify({"error": "Appointment not found"}), 404
    data = request.get_json() or {}
    try:
        customer = db.session.get(Customer, data.get("customer_id", a.customer_id))
        vehicle = db.session.get(Vehicle, data.get("vehicle_id", a.vehicle_id))
        service_ids = [int(x) for x in data.get("service_ids", [x.service_id for x in a.services])]
        services = Service.query.filter(Service.id.in_(service_ids), Service.is_active.is_(True)).all()
        if not customer or not vehicle or vehicle.customer_id != customer.id or len(services) != len(set(service_ids)):
            return jsonify({"error": "Invalid customer, vehicle or service data"}), 400
        start_at = parse_dt(data["start_at"]) if data.get("start_at") else a.start_at
        end_at = start_at + timedelta(minutes=sum(s.duration_minutes for s in services))
        if has_conflict(start_at, end_at, exclude_id=a.id):
            return jsonify({"error": "Appointment time conflicts with another appointment"}), 409
        status = data.get("status", a.status)
        if status not in STATUSES:
            return jsonify({"error": "Invalid status"}), 400
        a.customer_id, a.vehicle_id, a.start_at, a.end_at, a.status, a.notes = customer.id, vehicle.id, start_at, end_at, status, data.get("notes", a.notes)
        a.services.clear()
        db.session.flush()
        for service in services:
            db.session.add(AppointmentService(appointment_id=a.id, service_id=service.id, price=service.price, duration_minutes=service.duration_minutes))
        db.session.commit()
        return jsonify(serialize(a))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid appointment data"}), 400


@appointments_bp.delete("/<int:appointment_id>")
def delete_appointment(appointment_id):
    a = db.session.get(Appointment, appointment_id)
    if not a:
        return jsonify({"error": "Appointment not found"}), 404
    a.status = "cancelled"
    db.session.commit()
    return jsonify({"success": True})
