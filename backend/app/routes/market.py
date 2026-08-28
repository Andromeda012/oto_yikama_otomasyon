from collections import defaultdict
from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Product, Sale, SaleItem, Customer, Staff, AccountTransaction, StockMovement

market_bp = Blueprint("market_api", __name__, url_prefix="/api/market")
PAYMENT_METHODS = {"cash": "Nakit", "card": "Kart", "transfer": "Havale/EFT", "other": "Diğer"}


def product_json(product):
    stock = Decimal(product.stock_quantity or 0)
    minimum = Decimal(product.min_stock_level or 0)
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku or "",
        "unit": product.unit,
        "purchase_price": float(product.purchase_price or 0),
        "sale_price": float(product.sale_price or 0),
        "stock_quantity": float(stock),
        "min_stock_level": float(minimum),
        "is_active": bool(product.is_active),
        "low_stock": stock <= minimum,
        "out_of_stock": stock <= 0,
    }


def sale_json(sale):
    return {
        "id": sale.id,
        "customer": ({
            "id": sale.customer.id,
            "name": f"{sale.customer.first_name} {sale.customer.last_name}",
            "phone": sale.customer.phone,
        } if sale.customer else None),
        "staff": ({
            "id": sale.staff.id,
            "name": f"{sale.staff.first_name} {sale.staff.last_name}",
        } if sale.staff else None),
        "total_amount": float(sale.total_amount or 0),
        "status": sale.status,
        "payment_status": sale.payment_status,
        "payment_method": sale.payment_method,
        "payment_method_label": PAYMENT_METHODS.get(sale.payment_method, "-"),
        "created_at": sale.created_at.isoformat(),
        "items": [{
            "id": item.id,
            "product_id": item.product_id,
            "description": item.description,
            "quantity": float(item.quantity),
            "unit_price": float(item.unit_price),
            "line_total": float(item.line_total),
        } for item in sale.items],
    }


def error(message, status=400):
    return jsonify({"error": message}), status


@market_bp.get("/products")
def list_products():
    search = (request.args.get("search") or "").strip()
    query = Product.query.filter_by(is_active=True).order_by(Product.name.asc())
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Product.name.ilike(like), Product.sku.ilike(like)))
    return jsonify([product_json(p) for p in query.all()])


@market_bp.get("/lookups")
def lookups():
    customers = Customer.query.order_by(Customer.first_name, Customer.last_name).all()
    staff = Staff.query.filter_by(is_active=True).order_by(Staff.first_name, Staff.last_name).all()
    return jsonify({
        "customers": [{"id": c.id, "name": f"{c.first_name} {c.last_name}", "phone": c.phone} for c in customers],
        "staff": [{"id": s.id, "name": f"{s.first_name} {s.last_name}", "role": s.role or ""} for s in staff],
        "payment_methods": [{"value": key, "label": value} for key, value in PAYMENT_METHODS.items()],
    })


@market_bp.get("/sales")
def list_sales():
    limit = min(max(int(request.args.get("limit", 20)), 1), 100)
    sales = Sale.query.filter_by(status="completed").order_by(Sale.created_at.desc()).limit(limit).all()
    return jsonify([sale_json(sale) for sale in sales])


@market_bp.get("/summary")
def summary():
    product_count = Product.query.filter_by(is_active=True).count()
    low_stock = Product.query.filter(Product.is_active.is_(True), Product.stock_quantity <= Product.min_stock_level).count()
    today_total = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
        Sale.status == "completed",
        func.date(Sale.created_at) == func.current_date(),
    ).scalar()
    today_sales = Sale.query.filter(Sale.status == "completed", func.date(Sale.created_at) == func.current_date()).count()
    return jsonify({
        "product_count": product_count,
        "low_stock_count": low_stock,
        "today_sales": today_sales,
        "today_total": float(today_total or 0),
    })


@market_bp.get("/stock-movements")
def stock_movements():
    limit = min(max(int(request.args.get("limit", 50)), 1), 200)
    movements = StockMovement.query.order_by(StockMovement.created_at.desc(), StockMovement.id.desc()).limit(limit).all()
    return jsonify([{
        "id": item.id,
        "product_id": item.product_id,
        "product_name": item.product.name,
        "unit": item.product.unit,
        "sale_id": item.sale_id,
        "movement_type": item.movement_type,
        "quantity": float(item.quantity),
        "stock_before": float(item.stock_before),
        "stock_after": float(item.stock_after),
        "description": item.description or "",
        "created_at": item.created_at.isoformat(),
    } for item in movements])


@market_bp.post("/sales")
def create_sale():
    data = request.get_json() or {}
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        return error("Sepet boş olamaz.")

    customer_id = data.get("customer_id") or None
    staff_id = data.get("staff_id") or None
    payment_status = data.get("payment_status", "paid")
    payment_method = data.get("payment_method") or None

    if payment_status not in {"paid", "unpaid"}:
        return error("Geçersiz ödeme durumu.")
    if payment_status == "paid" and payment_method not in PAYMENT_METHODS:
        return error("Ödeme yöntemi seçilmelidir.")
    if payment_status == "unpaid" and not customer_id:
        return error("Veresiye satış için müşteri seçilmelidir.")

    customer = db.session.get(Customer, customer_id) if customer_id else None
    staff = db.session.get(Staff, staff_id) if staff_id else None
    if customer_id and not customer:
        return error("Müşteri bulunamadı.")
    if staff_id and not staff:
        return error("Personel bulunamadı.")

    quantities = defaultdict(Decimal)
    for item in raw_items:
        try:
            product_id = int(item.get("product_id"))
            quantity = Decimal(str(item.get("quantity", 0)))
        except (TypeError, ValueError, InvalidOperation):
            return error("Sepette geçersiz ürün veya miktar var.")
        if quantity <= 0:
            return error("Ürün miktarı sıfırdan büyük olmalıdır.")
        quantities[product_id] += quantity

    if not quantities:
        return error("Sepet boş olamaz.")

    try:
        products = Product.query.filter(Product.id.in_(list(quantities.keys())), Product.is_active.is_(True)).with_for_update().all()
        product_map = {p.id: p for p in products}
        if len(product_map) != len(quantities):
            return error("Sepetteki ürünlerden biri bulunamadı veya satışa kapalı.")

        total = Decimal("0")
        for product_id, quantity in quantities.items():
            product = product_map[product_id]
            stock = Decimal(product.stock_quantity or 0)
            if stock < quantity:
                raise ValueError(f"{product.name} için yeterli stok yok. Mevcut: {stock:g} {product.unit}.")
            total += Decimal(product.sale_price or 0) * quantity

        sale = Sale(
            customer_id=customer_id,
            staff_id=staff_id,
            total_amount=total,
            status="completed",
            payment_status=payment_status,
            payment_method=payment_method,
        )
        db.session.add(sale)
        db.session.flush()

        for product_id, quantity in quantities.items():
            product = product_map[product_id]
            before = Decimal(product.stock_quantity or 0)
            unit_price = Decimal(product.sale_price or 0)
            after = before - quantity
            product.stock_quantity = after
            db.session.add(SaleItem(
                sale_id=sale.id,
                line_type="product",
                product_id=product.id,
                description=product.name,
                quantity=quantity,
                unit_price=unit_price,
                line_total=unit_price * quantity,
            ))
            db.session.add(StockMovement(
                product_id=product.id,
                sale_id=sale.id,
                movement_type="sale",
                quantity=quantity,
                stock_before=before,
                stock_after=after,
                description=f"Market satışı #{sale.id}",
            ))

        if customer:
            db.session.add(AccountTransaction(
                customer_id=customer.id,
                sale_id=sale.id,
                transaction_type="debit",
                amount=total,
                description=f"Market satışı #{sale.id}",
            ))
            if payment_status == "paid":
                db.session.add(AccountTransaction(
                    customer_id=customer.id,
                    sale_id=sale.id,
                    transaction_type="payment",
                    amount=total,
                    description=f"Market satışı #{sale.id} ödeme - {PAYMENT_METHODS[payment_method]}",
                ))

        db.session.commit()
        return jsonify(sale_json(sale)), 201
    except ValueError as exc:
        db.session.rollback()
        return error(str(exc))
    except SQLAlchemyError:
        db.session.rollback()
        return error("Satış kaydedilirken veritabanı hatası oluştu.", 500)
