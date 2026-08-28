from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models import Customer, Product, Service, Staff, Vehicle

definitions_bp = Blueprint("definitions_api", __name__, url_prefix="/api/definitions")


def _json_error(message, status=400):
    return jsonify({"error": message}), status


def _decimal(value, field):
    try:
        amount = Decimal(str(value if value is not None else 0))
        if amount < 0:
            raise ValueError
        return amount
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"Invalid {field}")


def customer_json(c):
    return {
        "id": c.id, "first_name": c.first_name, "last_name": c.last_name,
        "name": f"{c.first_name} {c.last_name}", "phone": c.phone,
        "email": c.email or "", "notes": c.notes or "",
        "vehicle_count": len(c.vehicles),
    }


def vehicle_json(v):
    return {
        "id": v.id, "customer_id": v.customer_id, "plate": v.plate,
        "brand": v.brand or "", "model": v.model or "", "year": v.year,
        "color": v.color or "", "notes": v.notes or "",
        "customer_name": f"{v.customer.first_name} {v.customer.last_name}",
    }


def service_json(s):
    return {
        "id": s.id, "name": s.name, "price": float(s.price),
        "duration_minutes": s.duration_minutes, "is_active": s.is_active,
        "description": s.description or "",
    }


def staff_json(s):
    return {
        "id": s.id, "first_name": s.first_name, "last_name": s.last_name,
        "name": f"{s.first_name} {s.last_name}", "phone": s.phone or "",
        "role": s.role or "", "is_active": s.is_active,
    }


def product_json(p):
    return {
        "id": p.id, "name": p.name, "sku": p.sku or "", "unit": p.unit,
        "purchase_price": float(p.purchase_price or 0),
        "sale_price": float(p.sale_price or 0),
        "stock_quantity": float(p.stock_quantity or 0),
        "min_stock_level": float(p.min_stock_level or 0), "is_active": p.is_active,
    }


@definitions_bp.get("")
def list_definitions():
    try:
        return jsonify({
            "customers": [customer_json(x) for x in Customer.query.order_by(Customer.first_name, Customer.last_name).all()],
            "vehicles": [vehicle_json(x) for x in Vehicle.query.order_by(Vehicle.plate).all()],
            "services": [service_json(x) for x in Service.query.order_by(Service.name).all()],
            "staff": [staff_json(x) for x in Staff.query.order_by(Staff.first_name, Staff.last_name).all()],
            "products": [product_json(x) for x in Product.query.order_by(Product.name).all()],
        })
    except SQLAlchemyError as exc:
        db.session.rollback()
        return _json_error(f"Veritabanına bağlanılamadı: {exc}", 503)


@definitions_bp.post("/customers")
def create_customer():
    data = request.get_json() or {}
    first_name, last_name, phone = data.get("first_name", "").strip(), data.get("last_name", "").strip(), data.get("phone", "").strip()
    if not first_name or not last_name or not phone:
        return _json_error("Ad, soyad ve telefon zorunludur.")
    c = Customer(first_name=first_name, last_name=last_name, phone=phone, email=data.get("email"), notes=data.get("notes"))
    db.session.add(c)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("Müşteri kaydedilemedi.", 409)
    return jsonify(customer_json(c)), 201


@definitions_bp.put("/customers/<int:item_id>")
def update_customer(item_id):
    c = db.session.get(Customer, item_id)
    if not c:
        return _json_error("Müşteri bulunamadı.", 404)
    data = request.get_json() or {}
    first_name, last_name, phone = data.get("first_name", "").strip(), data.get("last_name", "").strip(), data.get("phone", "").strip()
    if not first_name or not last_name or not phone:
        return _json_error("Ad, soyad ve telefon zorunludur.")
    c.first_name, c.last_name, c.phone = first_name, last_name, phone
    c.email, c.notes = data.get("email"), data.get("notes")
    db.session.commit()
    return jsonify(customer_json(c))


@definitions_bp.delete("/customers/<int:item_id>")
def delete_customer(item_id):
    c = db.session.get(Customer, item_id)
    if not c:
        return _json_error("Müşteri bulunamadı.", 404)
    if c.vehicles:
        return _json_error("Aracı bulunan müşteri silinemez. Önce araçları taşıyın veya silin.", 409)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"success": True})


@definitions_bp.post("/vehicles")
def create_vehicle():
    data = request.get_json() or {}
    plate = data.get("plate", "").strip().upper()
    if not plate or not data.get("customer_id"):
        return _json_error("Plaka ve müşteri zorunludur.")
    customer = db.session.get(Customer, data.get("customer_id"))
    if not customer:
        return _json_error("Müşteri bulunamadı.", 404)
    v = Vehicle(customer_id=customer.id, plate=plate, brand=data.get("brand"), model=data.get("model"), year=data.get("year"), color=data.get("color"), notes=data.get("notes"))
    db.session.add(v)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("Bu plaka zaten kayıtlı.", 409)
    return jsonify(vehicle_json(v)), 201


@definitions_bp.put("/vehicles/<int:item_id>")
def update_vehicle(item_id):
    v = db.session.get(Vehicle, item_id)
    if not v:
        return _json_error("Araç bulunamadı.", 404)
    data = request.get_json() or {}
    plate = data.get("plate", "").strip().upper()
    customer = db.session.get(Customer, data.get("customer_id"))
    if not plate or not customer:
        return _json_error("Plaka ve müşteri zorunludur.")
    v.customer_id, v.plate = customer.id, plate
    v.brand, v.model, v.year, v.color, v.notes = data.get("brand"), data.get("model"), data.get("year"), data.get("color"), data.get("notes")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("Bu plaka zaten kayıtlı.", 409)
    return jsonify(vehicle_json(v))


@definitions_bp.delete("/vehicles/<int:item_id>")
def delete_vehicle(item_id):
    v = db.session.get(Vehicle, item_id)
    if not v:
        return _json_error("Araç bulunamadı.", 404)
    db.session.delete(v)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("Bu araç geçmiş kayıtlarda kullanıldığı için silinemiyor.", 409)
    return jsonify({"success": True})


@definitions_bp.post("/services")
def create_service():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return _json_error("Hizmet adı zorunludur.")
    try:
        s = Service(name=name, price=_decimal(data.get("price", 0), "price"), duration_minutes=int(data.get("duration_minutes", 30)), is_active=bool(data.get("is_active", True)), description=data.get("description"))
        if s.duration_minutes <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return _json_error("Fiyat ve süre değerlerini kontrol edin.")
    db.session.add(s)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("Bu hizmet zaten kayıtlı.", 409)
    return jsonify(service_json(s)), 201


@definitions_bp.put("/services/<int:item_id>")
def update_service(item_id):
    s = db.session.get(Service, item_id)
    if not s:
        return _json_error("Hizmet bulunamadı.", 404)
    data = request.get_json() or {}
    try:
        s.name = data.get("name", "").strip()
        s.price = _decimal(data.get("price", 0), "price")
        s.duration_minutes = int(data.get("duration_minutes", 30))
        s.is_active = bool(data.get("is_active", True))
        s.description = data.get("description")
        if not s.name or s.duration_minutes <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return _json_error("Hizmet bilgilerini kontrol edin.")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("Bu hizmet adı zaten kayıtlı.", 409)
    return jsonify(service_json(s))


@definitions_bp.delete("/services/<int:item_id>")
def delete_service(item_id):
    s = db.session.get(Service, item_id)
    if not s:
        return _json_error("Hizmet bulunamadı.", 404)
    s.is_active = False
    db.session.commit()
    return jsonify({"success": True})


@definitions_bp.post("/staff")
def create_staff():
    data = request.get_json() or {}
    first_name, last_name = data.get("first_name", "").strip(), data.get("last_name", "").strip()
    if not first_name or not last_name:
        return _json_error("Ad ve soyad zorunludur.")
    s = Staff(first_name=first_name, last_name=last_name, phone=data.get("phone"), role=data.get("role"), is_active=bool(data.get("is_active", True)))
    db.session.add(s)
    db.session.commit()
    return jsonify(staff_json(s)), 201


@definitions_bp.put("/staff/<int:item_id>")
def update_staff(item_id):
    s = db.session.get(Staff, item_id)
    if not s:
        return _json_error("Personel bulunamadı.", 404)
    data = request.get_json() or {}
    s.first_name, s.last_name = data.get("first_name", "").strip(), data.get("last_name", "").strip()
    s.phone, s.role, s.is_active = data.get("phone"), data.get("role"), bool(data.get("is_active", True))
    if not s.first_name or not s.last_name:
        return _json_error("Ad ve soyad zorunludur.")
    db.session.commit()
    return jsonify(staff_json(s))


@definitions_bp.delete("/staff/<int:item_id>")
def delete_staff(item_id):
    s = db.session.get(Staff, item_id)
    if not s:
        return _json_error("Personel bulunamadı.", 404)
    s.is_active = False
    db.session.commit()
    return jsonify({"success": True})


@definitions_bp.post("/products")
def create_product():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return _json_error("Ürün adı zorunludur.")
    try:
        p = Product(name=name, sku=data.get("sku") or None, unit=data.get("unit", "adet"), purchase_price=_decimal(data.get("purchase_price", 0), "purchase_price"), sale_price=_decimal(data.get("sale_price", 0), "sale_price"), stock_quantity=_decimal(data.get("stock_quantity", 0), "stock_quantity"), min_stock_level=_decimal(data.get("min_stock_level", 0), "min_stock_level"), is_active=bool(data.get("is_active", True)))
    except (ValueError, TypeError):
        return _json_error("Ürün değerlerini kontrol edin.")
    db.session.add(p)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("SKU zaten kayıtlı.", 409)
    except SQLAlchemyError as exc:
        db.session.rollback()
        return _json_error(f"Veritabanına ürün kaydedilemedi: {exc}", 503)
    return jsonify(product_json(p)), 201


@definitions_bp.put("/products/<int:item_id>")
def update_product(item_id):
    p = db.session.get(Product, item_id)
    if not p:
        return _json_error("Ürün bulunamadı.", 404)
    data = request.get_json() or {}
    try:
        p.name = data.get("name", "").strip()
        p.sku = data.get("sku") or None
        p.unit = data.get("unit", "adet")
        p.purchase_price = _decimal(data.get("purchase_price", 0), "purchase_price")
        p.sale_price = _decimal(data.get("sale_price", 0), "sale_price")
        p.stock_quantity = _decimal(data.get("stock_quantity", 0), "stock_quantity")
        p.min_stock_level = _decimal(data.get("min_stock_level", 0), "min_stock_level")
        p.is_active = bool(data.get("is_active", True))
        if not p.name:
            raise ValueError
    except (ValueError, TypeError):
        return _json_error("Ürün değerlerini kontrol edin.")
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _json_error("SKU zaten kayıtlı.", 409)
    except SQLAlchemyError as exc:
        db.session.rollback()
        return _json_error(f"Veritabanında ürün güncellenemedi: {exc}", 503)
    return jsonify(product_json(p))


@definitions_bp.delete("/products/<int:item_id>")
def delete_product(item_id):
    p = db.session.get(Product, item_id)
    if not p:
        return _json_error("Ürün bulunamadı.", 404)
    p.is_active = False
    db.session.commit()
    return jsonify({"success": True})
