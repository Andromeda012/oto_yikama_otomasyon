from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models import Appointment, Product, Sale, VehicleJob, Customer


dashboard_bp = Blueprint("dashboard_api", __name__, url_prefix="/api/dashboard")

ACTIVE_APPOINTMENT_STATUSES = {"scheduled", "arrived", "in_service"}
ACTIVE_JOB_STATUSES = {"waiting", "checked_in", "washing", "quality_check", "ready"}


def _day_range(value=None):
    if value:
        day = datetime.fromisoformat(value)
    else:
        day = datetime.now()
    day = day.replace(hour=0, minute=0, second=0, microsecond=0)
    return day, day + timedelta(days=1)


def _appointment_json(item):
    services = sorted(item.services, key=lambda x: x.service.name.lower())
    return {
        "id": item.id,
        "time": item.start_at.strftime("%H:%M"),
        "start_at": item.start_at.isoformat(),
        "status": item.status,
        "customer": f"{item.customer.first_name} {item.customer.last_name}",
        "plate": item.vehicle.plate,
        "vehicle": " ".join(x for x in [item.vehicle.brand, item.vehicle.model] if x) or "Araç",
        "services": [x.service.name for x in services],
        "total_price": float(sum((x.price for x in services), 0)),
    }


@dashboard_bp.get("")
def dashboard_summary():
    try:
        start, end = _day_range(request.args.get("date"))
    except ValueError:
        return jsonify({"error": "Geçersiz tarih."}), 400

    appointment_count = Appointment.query.filter(
        Appointment.start_at >= start,
        Appointment.start_at < end,
        Appointment.status != "cancelled",
    ).count()

    waiting_appointments = Appointment.query.filter(
        Appointment.start_at >= start,
        Appointment.start_at < end,
        Appointment.status.in_(["scheduled", "arrived"]),
    ).count()

    job_query = VehicleJob.query.filter(
        VehicleJob.created_at >= start,
        VehicleJob.created_at < end,
    )
    active_jobs = job_query.filter(VehicleJob.status.in_(ACTIVE_JOB_STATUSES)).count()
    waiting_jobs = job_query.filter(VehicleJob.status.in_(["waiting", "checked_in"])).count()
    washing_jobs = job_query.filter(VehicleJob.status == "washing").count()
    ready_jobs = job_query.filter(VehicleJob.status == "ready").count()
    inspection_jobs = job_query.filter(VehicleJob.status == "quality_check").count()

    market_revenue = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.created_at >= start,
        Sale.created_at < end,
        Sale.status == "completed",
        Sale.vehicle_job_id.is_(None),
    ).scalar() or 0

    service_revenue = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.created_at >= start,
        Sale.created_at < end,
        Sale.status == "completed",
        Sale.vehicle_job_id.is_not(None),
    ).scalar() or 0

    low_stock = Product.query.filter(
        Product.is_active.is_(True),
        Product.stock_quantity <= Product.min_stock_level,
    ).count()

    customer_count = Customer.query.count()

    appointments = Appointment.query.filter(
        Appointment.start_at >= start,
        Appointment.start_at < end,
        Appointment.status != "cancelled",
    ).order_by(Appointment.start_at.asc()).limit(8).all()

    return jsonify({
        "date": start.date().isoformat(),
        "summary": {
            "appointment_count": appointment_count,
            "waiting_appointments": waiting_appointments,
            "active_jobs": active_jobs,
            "waiting_jobs": waiting_jobs,
            "washing_jobs": washing_jobs,
            "ready_jobs": ready_jobs,
            "inspection_jobs": inspection_jobs,
            "today_revenue": float(market_revenue) + float(service_revenue),
            "market_revenue": float(market_revenue),
            "service_revenue": float(service_revenue),
            "low_stock_count": low_stock,
            "customer_count": customer_count,
        },
        "appointments": [_appointment_json(item) for item in appointments],
    })
