from datetime import datetime, timedelta
from decimal import Decimal

from flask import Blueprint, jsonify, request
from sqlalchemy import case, desc, func

from app.extensions import db
from app.models import (
    AccountTransaction,
    Appointment,
    Customer,
    Product,
    Sale,
    SaleItem,
    Service,
    Staff,
    Vehicle,
    VehicleJob,
    VehicleJobService,
)

statistics_bp = Blueprint("statistics_api", __name__, url_prefix="/api/statistics")


STATUS_LABELS = {
    "scheduled": "Planlandı",
    "arrived": "Geldi",
    "in_service": "İşlemde",
    "cancelled": "İptal",
    "completed": "Tamamlandı",
    "waiting": "Bekliyor",
    "checked_in": "İşleme Alındı",
    "washing": "Yıkamada",
    "quality_check": "Kontrol",
    "ready": "Hazır",
    "delivered": "Teslim Edildi",
}


def _parse_period():
    preset = (request.args.get("period") or "month").lower()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    if preset == "today":
        start = today
        end = today + timedelta(days=1)
    elif preset == "week":
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=7)
    elif preset == "year":
        start = today.replace(month=1, day=1)
        end = start.replace(year=start.year + 1)
    elif preset == "custom":
        try:
            start = datetime.fromisoformat(request.args["start"]).replace(hour=0, minute=0, second=0, microsecond=0)
            end = datetime.fromisoformat(request.args["end"]).replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        except (KeyError, ValueError):
            raise ValueError("Geçerli bir başlangıç ve bitiş tarihi girin.")
    else:
        preset = "month"
        start = today.replace(day=1)
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)

    if end <= start:
        raise ValueError("Bitiş tarihi başlangıç tarihinden sonra olmalıdır.")
    return preset, start, end


def _money(value):
    return float(Decimal(value or 0))


def _period_previous(start, end):
    length = end - start
    return start - length, start


def _percent_change(current, previous):
    current = float(current or 0)
    previous = float(previous or 0)
    if previous == 0:
        return 100.0 if current else 0.0
    return round(((current - previous) / previous) * 100, 1)


def _sale_totals(start, end):
    total = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed"
    ).scalar() or 0
    service = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed", Sale.vehicle_job_id.is_not(None)
    ).scalar() or 0
    market = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed", Sale.vehicle_job_id.is_(None)
    ).scalar() or 0
    count = Sale.query.filter(Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed").count()
    return Decimal(total), Decimal(service), Decimal(market), count


@statistics_bp.get("")
def statistics_summary():
    try:
        preset, start, end = _parse_period()
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    previous_start, previous_end = _period_previous(start, end)
    revenue, service_revenue, market_revenue, sale_count = _sale_totals(start, end)
    previous_revenue, _, _, _ = _sale_totals(previous_start, previous_end)

    appointment_count = Appointment.query.filter(
        Appointment.start_at >= start, Appointment.start_at < end, Appointment.status != "cancelled"
    ).count()
    completed_appointments = Appointment.query.filter(
        Appointment.start_at >= start, Appointment.start_at < end, Appointment.status == "completed"
    ).count()
    cancelled_appointments = Appointment.query.filter(
        Appointment.start_at >= start, Appointment.start_at < end, Appointment.status == "cancelled"
    ).count()

    delivered_jobs = VehicleJob.query.filter(
        VehicleJob.delivered_at >= start, VehicleJob.delivered_at < end, VehicleJob.status == "delivered"
    ).count()

    active_customer_count = Customer.query.count()
    vehicle_count = Vehicle.query.count()

    debit = db.session.query(func.coalesce(func.sum(AccountTransaction.amount), 0)).filter(
        AccountTransaction.created_at >= start,
        AccountTransaction.created_at < end,
        AccountTransaction.transaction_type == "debit",
    ).scalar() or 0
    payments = db.session.query(func.coalesce(func.sum(AccountTransaction.amount), 0)).filter(
        AccountTransaction.created_at >= start,
        AccountTransaction.created_at < end,
        AccountTransaction.transaction_type.in_(["payment", "credit"]),
    ).scalar() or 0

    low_stock = Product.query.filter(Product.is_active.is_(True), Product.stock_quantity <= Product.min_stock_level).count()

    status_rows = db.session.query(VehicleJob.status, func.count(VehicleJob.id)).filter(
        VehicleJob.status != "cancelled"
    ).group_by(VehicleJob.status).all()

    service_rows = db.session.query(
        Service.id,
        Service.name,
        func.coalesce(func.sum(SaleItem.quantity), 0),
        func.coalesce(func.sum(SaleItem.line_total), 0),
    ).join(SaleItem, SaleItem.service_id == Service.id).join(Sale, Sale.id == SaleItem.sale_id).filter(
        Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed", SaleItem.line_type == "service"
    ).group_by(Service.id, Service.name).order_by(desc(func.sum(SaleItem.line_total))).limit(10).all()

    product_rows = db.session.query(
        Product.id,
        Product.name,
        Product.unit,
        func.coalesce(func.sum(SaleItem.quantity), 0),
        func.coalesce(func.sum(SaleItem.line_total), 0),
    ).join(SaleItem, SaleItem.product_id == Product.id).join(Sale, Sale.id == SaleItem.sale_id).filter(
        Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed", SaleItem.line_type == "product"
    ).group_by(Product.id, Product.name, Product.unit).order_by(desc(func.sum(SaleItem.line_total))).limit(10).all()

    payment_rows = db.session.query(
        Sale.payment_method,
        func.count(Sale.id),
        func.coalesce(func.sum(Sale.total_amount), 0),
    ).filter(
        Sale.created_at >= start, Sale.created_at < end, Sale.status == "completed"
    ).group_by(Sale.payment_method).order_by(desc(func.sum(Sale.total_amount))).all()

    staff_rows = db.session.query(
        Staff.id,
        Staff.first_name,
        Staff.last_name,
        func.count(VehicleJob.id),
        func.coalesce(func.sum(Sale.total_amount), 0),
    ).join(VehicleJob, VehicleJob.staff_id == Staff.id).outerjoin(Sale, Sale.vehicle_job_id == VehicleJob.id).filter(
        VehicleJob.created_at >= start, VehicleJob.created_at < end
    ).group_by(Staff.id, Staff.first_name, Staff.last_name).order_by(desc(func.count(VehicleJob.id))).limit(10).all()

    # Daily revenue is intentionally built in Python for MySQL compatibility across versions/timezones.
    daily = []
    cursor = start
    while cursor < end:
        next_day = cursor + timedelta(days=1)
        amount = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.created_at >= cursor, Sale.created_at < next_day, Sale.status == "completed"
        ).scalar() or 0
        daily.append({"date": cursor.date().isoformat(), "label": cursor.strftime("%d %b"), "revenue": _money(amount)})
        cursor = next_day
        if len(daily) > 370:
            break

    return jsonify({
        "period": {"preset": preset, "start": start.date().isoformat(), "end": (end - timedelta(days=1)).date().isoformat()},
        "summary": {
            "revenue": _money(revenue),
            "service_revenue": _money(service_revenue),
            "market_revenue": _money(market_revenue),
            "sale_count": sale_count,
            "average_sale": _money(revenue / sale_count if sale_count else 0),
            "revenue_change": _percent_change(revenue, previous_revenue),
            "appointment_count": appointment_count,
            "completed_appointments": completed_appointments,
            "cancelled_appointments": cancelled_appointments,
            "delivered_jobs": delivered_jobs,
            "customer_count": active_customer_count,
            "vehicle_count": vehicle_count,
            "period_debit": _money(debit),
            "period_payments": _money(payments),
            "low_stock_count": low_stock,
        },
        "daily_revenue": daily,
        "services": [
            {"id": r[0], "name": r[1], "quantity": _money(r[2]), "revenue": _money(r[3])}
            for r in service_rows
        ],
        "products": [
            {"id": r[0], "name": r[1], "unit": r[2], "quantity": _money(r[3]), "revenue": _money(r[4])}
            for r in product_rows
        ],
        "payments": [
            {"method": r[0] or "unspecified", "count": int(r[1]), "revenue": _money(r[2])}
            for r in payment_rows
        ],
        "staff": [
            {"id": r[0], "name": f"{r[1]} {r[2]}", "jobs": int(r[3]), "revenue": _money(r[4])}
            for r in staff_rows
        ],
        "job_statuses": [
            {"status": status, "label": STATUS_LABELS.get(status, status), "count": int(count)}
            for status, count in status_rows
        ],
    })
