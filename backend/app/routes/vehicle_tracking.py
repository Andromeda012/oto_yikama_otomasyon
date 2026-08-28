from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import (
    Appointment, AppointmentService, Customer, Product, Service, Staff, Vehicle,
    VehicleJob, VehicleJobService, VehicleJobStatusHistory,
    Sale, SaleItem, AccountTransaction, StockMovement,
)

vehicle_tracking_bp = Blueprint("vehicle_tracking_api", __name__, url_prefix="/api/vehicle-tracking")

STATUSES = {
    "waiting": "Bekliyor",
    "checked_in": "İşleme Alındı",
    "washing": "Yıkamada",
    "quality_check": "Kontrol",
    "ready": "Hazır",
    "delivered": "Teslim Edildi",
    "cancelled": "İptal",
}
ACTIVE_STATUSES = {"waiting", "checked_in", "washing", "quality_check", "ready"}

ALLOWED_TRANSITIONS = {
    "waiting": {"checked_in", "cancelled"},
    "checked_in": {"washing", "cancelled"},
    "washing": {"quality_check", "cancelled"},
    "quality_check": {"ready", "washing", "cancelled"},
    "ready": {"delivered", "washing"},
}


def parse_dt(value, required=True):
    if not value:
        if required:
            raise ValueError("Başlangıç zamanı zorunludur.")
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)


def service_ids_from_data(data, appointment=None):
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


def validate_entities(data, service_ids):
    customer = db.session.get(Customer, data.get("customer_id"))
    vehicle = db.session.get(Vehicle, data.get("vehicle_id"))
    if not customer:
        raise ValueError("Müşteri bulunamadı.")
    if not vehicle or vehicle.customer_id != customer.id:
        raise ValueError("Seçilen araç bu müşteriye ait değil.")

    services = Service.query.filter(Service.id.in_(service_ids), Service.is_active.is_(True)).all()
    service_map = {service.id: service for service in services}
    if len(service_map) != len(service_ids):
        raise ValueError("Seçilen hizmetlerden biri geçersiz veya pasif.")
    return customer, vehicle, [service_map[item] for item in service_ids]


def serialize(job):
    services = sorted(job.services, key=lambda item: item.service.name.lower())
    return {
        "id": job.id,
        "appointment_id": job.appointment_id,
        "customer": {
            "id": job.customer.id,
            "name": f"{job.customer.first_name} {job.customer.last_name}",
            "phone": job.customer.phone,
        },
        "vehicle": {
            "id": job.vehicle.id,
            "plate": job.vehicle.plate,
            "brand": job.vehicle.brand or "",
            "model": job.vehicle.model or "",
            "color": job.vehicle.color or "",
        },
        "staff": ({
            "id": job.staff.id,
            "name": f"{job.staff.first_name} {job.staff.last_name}",
            "role": job.staff.role or "",
        } if job.staff else None),
        "status": job.status,
        "status_label": STATUSES.get(job.status, job.status),
        "priority": job.priority,
        "check_in_at": job.check_in_at.isoformat() if job.check_in_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "estimated_end_at": job.estimated_end_at.isoformat() if job.estimated_end_at else None,
        "ready_at": job.ready_at.isoformat() if job.ready_at else None,
        "delivered_at": job.delivered_at.isoformat() if job.delivered_at else None,
        "notes": job.notes or "",
        "created_at": job.created_at.isoformat(),
        "total_price": sum(float(x.price) for x in services),
        "total_duration_minutes": sum(x.duration_minutes for x in services),
        "financial": ({
            "sale_id": job.sale.id,
            "total_amount": float(job.sale.total_amount),
            "payment_status": job.sale.payment_status,
        } if job.sale else None),
        "services": [{
            "id": x.service.id,
            "name": x.service.name,
            "price": float(x.price),
            "duration_minutes": x.duration_minutes,
        } for x in services],
    }


def add_history(job, status, note=None):
    db.session.add(VehicleJobStatusHistory(
        job_id=job.id,
        status=status,
        note=note,
    ))


def sync_appointment_status(job, status):
    if not job.appointment:
        return
    mapped = {
        "checked_in": "arrived",
        "washing": "in_service",
        "quality_check": "in_service",
        "ready": "in_service",
        "delivered": "completed",
        "cancelled": "cancelled",
    }
    target = mapped.get(status)
    if target:
        job.appointment.status = target


def apply_timestamps(job, status, previous_status=None):
    now = datetime.utcnow()
    if status == "checked_in" and not job.check_in_at:
        job.check_in_at = now
    if status == "washing" and not job.started_at:
        job.started_at = now
    if status == "ready":
        job.ready_at = job.ready_at or now
    if status == "delivered":
        job.delivered_at = job.delivered_at or now


def attach_services(job, services):
    job.services.clear()
    db.session.flush()
    for service in services:
        db.session.add(VehicleJobService(
            job_id=job.id,
            service_id=service.id,
            price=service.price,
            duration_minutes=service.duration_minutes,
        ))


def active_job_for_vehicle(vehicle_id, exclude_id=None):
    query = VehicleJob.query.filter(
        VehicleJob.vehicle_id == vehicle_id,
        VehicleJob.status.in_(ACTIVE_STATUSES),
    )
    if exclude_id is not None:
        query = query.filter(VehicleJob.id != exclude_id)
    return query.order_by(VehicleJob.created_at.desc()).first()


@vehicle_tracking_bp.get("")
def list_jobs():
    date = request.args.get("date")
    status = request.args.get("status")
    query = VehicleJob.query.order_by(VehicleJob.priority.desc(), VehicleJob.created_at.asc())

    if date:
        try:
            day = datetime.fromisoformat(date)
        except ValueError:
            return jsonify({"error": "Geçersiz tarih."}), 400
        query = query.filter(VehicleJob.created_at >= day, VehicleJob.created_at < day + timedelta(days=1))
    if status and status in STATUSES:
        query = query.filter(VehicleJob.status == status)

    return jsonify([serialize(job) for job in query.all()])


@vehicle_tracking_bp.get("/available-appointments")
def available_appointments():
    date = request.args.get("date")
    query = Appointment.query.filter(Appointment.status.in_({"scheduled", "arrived"})).order_by(Appointment.start_at.asc())
    if date:
        try:
            day = datetime.fromisoformat(date)
        except ValueError:
            return jsonify({"error": "Geçersiz tarih."}), 400
        query = query.filter(Appointment.start_at >= day, Appointment.start_at < day + timedelta(days=1))
    appointments = []
    for appointment in query.all():
        if appointment.vehicle_job:
            continue
        appointments.append({
            "id": appointment.id,
            "start_at": appointment.start_at.isoformat(),
            "status": appointment.status,
            "customer": {"id": appointment.customer.id, "name": f"{appointment.customer.first_name} {appointment.customer.last_name}", "phone": appointment.customer.phone},
            "vehicle": {"id": appointment.vehicle.id, "plate": appointment.vehicle.plate, "brand": appointment.vehicle.brand or "", "model": appointment.vehicle.model or ""},
            "services": [{"id": item.service.id, "name": item.service.name} for item in appointment.services],
        })
    return jsonify(appointments)


@vehicle_tracking_bp.get("/lookups")
def lookups():
    customers = Customer.query.order_by(Customer.first_name, Customer.last_name).all()
    vehicles = Vehicle.query.order_by(Vehicle.plate).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
    staff = Staff.query.filter_by(is_active=True).order_by(Staff.first_name, Staff.last_name).all()
    return jsonify({
        "customers": [{"id": c.id, "name": f"{c.first_name} {c.last_name}", "phone": c.phone} for c in customers],
        "vehicles": [{"id": v.id, "customer_id": v.customer_id, "plate": v.plate, "brand": v.brand or "", "model": v.model or "", "color": v.color or ""} for v in vehicles],
        "services": [{"id": s.id, "name": s.name, "price": float(s.price), "duration_minutes": s.duration_minutes} for s in services],
        "staff": [{"id": s.id, "name": f"{s.first_name} {s.last_name}", "role": s.role or ""} for s in staff],
    })


@vehicle_tracking_bp.post("")
def create_job():
    data = request.get_json() or {}
    try:
        appointment = db.session.get(Appointment, data.get("appointment_id")) if data.get("appointment_id") else None
        service_ids = service_ids_from_data(data, appointment)
        if appointment:
            data = {**data, "customer_id": appointment.customer_id, "vehicle_id": appointment.vehicle_id}
            if appointment.status == "cancelled":
                raise ValueError("İptal edilmiş randevu işleme alınamaz.")

        customer, vehicle, services = validate_entities(data, service_ids)
        if active_job_for_vehicle(vehicle.id):
            raise ValueError("Bu araç için zaten aktif bir takip kaydı bulunuyor.")

        status = data.get("status", "waiting")
        if status not in STATUSES:
            raise ValueError("Geçersiz araç takip durumu.")
        if status == "delivered":
            raise ValueError("Yeni iş emri teslim edildi olarak oluşturulamaz.")

        start_at = parse_dt(data.get("start_at"), required=False)
        duration = sum(s.duration_minutes for s in services)
        estimated_end = start_at + timedelta(minutes=duration) if start_at else None
        job = VehicleJob(
            appointment_id=appointment.id if appointment else None,
            customer_id=customer.id,
            vehicle_id=vehicle.id,
            staff_id=data.get("staff_id") or None,
            status=status,
            priority=int(data.get("priority", 0) or 0),
            check_in_at=start_at if status == "checked_in" and start_at else None,
            estimated_end_at=estimated_end,
            notes=(data.get("notes") or "").strip() or None,
        )
        db.session.add(job)
        db.session.flush()
        attach_services(job, services)
        apply_timestamps(job, status)
        add_history(job, status, "İş emri oluşturuldu.")
        sync_appointment_status(job, status)
        if status == "delivered":
            create_delivery_sale(job)
        db.session.commit()
        return jsonify(serialize(job)), 201
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Geçersiz araç takip bilgileri."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "İş emri kaydedilirken veritabanı hatası oluştu."}), 500


@vehicle_tracking_bp.post("/from-appointment/<int:appointment_id>")
def create_from_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        return jsonify({"error": "Randevu bulunamadı."}), 404
    if appointment.status == "cancelled":
        return jsonify({"error": "İptal edilmiş randevu işleme alınamaz."}), 400
    existing = VehicleJob.query.filter_by(appointment_id=appointment.id).first()
    if existing:
        return jsonify(serialize(existing)), 200

    try:
        services = [item.service for item in appointment.services]
        if not services:
            raise ValueError("Randevuda hizmet bulunmuyor.")
        if active_job_for_vehicle(appointment.vehicle_id):
            raise ValueError("Bu araç için zaten aktif bir takip kaydı bulunuyor.")
        duration = sum(s.duration_minutes for s in services)
        job = VehicleJob(
            appointment_id=appointment.id,
            customer_id=appointment.customer_id,
            vehicle_id=appointment.vehicle_id,
            status="checked_in",
            check_in_at=datetime.utcnow(),
            estimated_end_at=datetime.utcnow() + timedelta(minutes=duration),
            notes=appointment.notes,
        )
        db.session.add(job)
        db.session.flush()
        attach_services(job, services)
        add_history(job, "checked_in", "Randevudan işleme alındı.")
        appointment.status = "arrived"
        db.session.commit()
        return jsonify(serialize(job)), 201
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Randevu işleme alınamadı."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "İş emri oluşturulurken veritabanı hatası oluştu."}), 500


def create_delivery_sale(job):
    """Create the service sale and customer debit exactly once when a job is delivered."""
    existing = Sale.query.filter_by(vehicle_job_id=job.id).first()
    if existing:
        return existing

    total = sum((float(item.price) for item in job.services), 0.0)

    # Consume mapped service materials exactly once, as part of the same transaction.
    material_requirements = defaultdict(Decimal)
    for job_service in job.services:
        for material in job_service.service.materials:
            material_requirements[material.product_id] += Decimal(material.quantity or 0)
    if material_requirements:
        products = Product.query.filter(Product.id.in_(list(material_requirements.keys())), Product.is_active.is_(True)).with_for_update().all()
        product_map = {product.id: product for product in products}
        if len(product_map) != len(material_requirements):
            raise ValueError("Hizmet malzemelerinden biri bulunamadı veya pasif.")
        for product_id, required in material_requirements.items():
            product = product_map[product_id]
            before = Decimal(product.stock_quantity or 0)
            if before < required:
                raise ValueError(f"{product.name} için hizmet tüketimi sonrası yeterli stok yok. Gerekli: {required:g} {product.unit}, mevcut: {before:g} {product.unit}.")
        for product_id, required in material_requirements.items():
            product = product_map[product_id]
            before = Decimal(product.stock_quantity or 0)
            after = before - required
            product.stock_quantity = after
            db.session.add(StockMovement(
                product_id=product.id,
                movement_type="service_consumption",
                quantity=required,
                stock_before=before,
                stock_after=after,
                description=f"İş emri #{job.id} - hizmet tüketimi",
            ))

    sale = Sale(
        customer_id=job.customer_id,
        staff_id=job.staff_id,
        vehicle_job_id=job.id,
        total_amount=total,
        status="completed",
        payment_status="unpaid",
    )
    db.session.add(sale)
    db.session.flush()

    for item in job.services:
        db.session.add(SaleItem(
            sale_id=sale.id,
            line_type="service",
            service_id=item.service_id,
            description=item.service.name,
            quantity=1,
            unit_price=item.price,
            line_total=item.price,
        ))

    if total > 0:
        db.session.add(AccountTransaction(
            customer_id=job.customer_id,
            sale_id=sale.id,
            vehicle_job_id=job.id,
            transaction_type="debit",
            amount=total,
            description=f"Araç hizmeti #{job.id} - {job.vehicle.plate}",
        ))
    return sale


@vehicle_tracking_bp.get("/<int:job_id>/financial")
def get_financial(job_id):
    job = db.session.get(VehicleJob, job_id)
    if not job:
        return jsonify({"error": "Araç takip kaydı bulunamadı."}), 404
    sale = Sale.query.filter_by(vehicle_job_id=job.id).first()
    if not sale:
        return jsonify({
            "sale": None,
            "total_amount": sum(float(item.price) for item in job.services),
            "payment_status": "not_created",
        })
    return jsonify({
        "sale": {
            "id": sale.id,
            "status": sale.status,
            "payment_status": sale.payment_status,
            "total_amount": float(sale.total_amount),
            "created_at": sale.created_at.isoformat(),
            "items": [{
                "description": item.description,
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "line_total": float(item.line_total),
            } for item in sale.items],
        },
        "total_amount": float(sale.total_amount),
        "payment_status": sale.payment_status,
    })


@vehicle_tracking_bp.patch("/<int:job_id>/payment")
def mark_paid(job_id):
    job = db.session.get(VehicleJob, job_id)
    if not job:
        return jsonify({"error": "Araç takip kaydı bulunamadı."}), 404
    sale = Sale.query.filter_by(vehicle_job_id=job.id).first()
    if not sale:
        return jsonify({"error": "Bu iş emrine ait satış kaydı bulunamadı."}), 400
    if sale.payment_status == "paid":
        return jsonify({"message": "Satış zaten ödenmiş.", "sale_id": sale.id, "payment_status": sale.payment_status})
    data = request.get_json() or {}
    payment_method = data.get("payment_method") or "cash"
    if payment_method not in {"cash", "card", "transfer", "other"}:
        return jsonify({"error": "Geçersiz ödeme yöntemi."}), 400
    try:
        sale.payment_status = "paid"
        sale.payment_method = payment_method
        labels = {"cash": "Nakit", "card": "Kart", "transfer": "Havale/EFT", "other": "Diğer"}
        db.session.add(AccountTransaction(
            customer_id=job.customer_id,
            sale_id=sale.id,
            vehicle_job_id=job.id,
            transaction_type="payment",
            amount=sale.total_amount,
            description=f"Araç hizmeti #{job.id} ödeme - {job.vehicle.plate} - {labels[payment_method]}",
        ))
        db.session.commit()
        return jsonify({"sale_id": sale.id, "payment_status": sale.payment_status})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Ödeme kaydedilirken veritabanı hatası oluştu."}), 500


@vehicle_tracking_bp.patch("/<int:job_id>/status")
def update_status(job_id):
    job = db.session.get(VehicleJob, job_id)
    if not job:
        return jsonify({"error": "Araç takip kaydı bulunamadı."}), 404
    data = request.get_json() or {}
    status = data.get("status")
    if status not in STATUSES:
        return jsonify({"error": "Geçersiz araç takip durumu."}), 400
    if job.status == status:
        return jsonify(serialize(job))
    if job.status in {"delivered", "cancelled"}:
        return jsonify({"error": "Tamamlanmış veya iptal edilmiş kayıt değiştirilemez."}), 400
    if status not in ALLOWED_TRANSITIONS.get(job.status, set()):
        return jsonify({"error": f"{STATUSES.get(job.status, job.status)} durumundan {STATUSES.get(status, status)} durumuna geçiş yapılamaz."}), 400

    try:
        previous = job.status
        job.status = status
        if data.get("staff_id"):
            job.staff_id = int(data["staff_id"])
        apply_timestamps(job, status, previous)
        add_history(job, status, data.get("note"))
        sync_appointment_status(job, status)
        if status == "delivered":
            create_delivery_sale(job)
        db.session.commit()
        return jsonify(serialize(job))
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Geçersiz durum bilgisi."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Durum güncellenirken veritabanı hatası oluştu."}), 500


@vehicle_tracking_bp.put("/<int:job_id>")
def update_job(job_id):
    job = db.session.get(VehicleJob, job_id)
    if not job:
        return jsonify({"error": "Araç takip kaydı bulunamadı."}), 404
    if job.status in {"delivered", "cancelled"}:
        return jsonify({"error": "Tamamlanmış veya iptal edilmiş kayıt değiştirilemez."}), 400
    data = request.get_json() or {}
    try:
        service_ids = service_ids_from_data(data, job.appointment)
        entity_data = {"customer_id": data.get("customer_id", job.customer_id), "vehicle_id": data.get("vehicle_id", job.vehicle_id)}
        customer, vehicle, services = validate_entities(entity_data, service_ids)
        conflict = active_job_for_vehicle(vehicle.id, exclude_id=job.id)
        if conflict:
            raise ValueError("Bu araç için başka bir aktif takip kaydı bulunuyor.")
        job.customer_id = customer.id
        job.vehicle_id = vehicle.id
        job.staff_id = data.get("staff_id") or None
        job.priority = int(data.get("priority", job.priority) or 0)
        job.notes = (data.get("notes", job.notes or "") or "").strip() or None
        attach_services(job, services)
        if data.get("estimated_end_at"):
            job.estimated_end_at = parse_dt(data["estimated_end_at"])
        db.session.commit()
        return jsonify(serialize(job))
    except (ValueError, TypeError):
        db.session.rollback()
        return jsonify({"error": "Geçersiz takip bilgileri."}), 400
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"error": "Takip kaydı güncellenirken veritabanı hatası oluştu."}), 500


@vehicle_tracking_bp.get("/<int:job_id>/history")
def history(job_id):
    job = db.session.get(VehicleJob, job_id)
    if not job:
        return jsonify({"error": "Araç takip kaydı bulunamadı."}), 404
    rows = VehicleJobStatusHistory.query.filter_by(job_id=job.id).order_by(VehicleJobStatusHistory.changed_at.asc()).all()
    return jsonify([{
        "id": row.id,
        "status": row.status,
        "status_label": STATUSES.get(row.status, row.status),
        "note": row.note or "",
        "changed_at": row.changed_at.isoformat(),
    } for row in rows])
