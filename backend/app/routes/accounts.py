from decimal import Decimal, InvalidOperation
from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import AccountTransaction, Customer, Sale

accounts_bp = Blueprint("accounts_api", __name__, url_prefix="/api/accounts")

PAYMENT_METHODS = {
    "cash": "Nakit",
    "card": "Kart",
    "transfer": "Havale/EFT",
    "other": "Diğer",
}


def money(value):
    return float(Decimal(value or 0))


def balance_for(customer_id):
    debit = db.session.query(func.coalesce(func.sum(AccountTransaction.amount), 0)).filter(
        AccountTransaction.customer_id == customer_id,
        AccountTransaction.transaction_type == "debit",
    ).scalar()
    credit = db.session.query(func.coalesce(func.sum(AccountTransaction.amount), 0)).filter(
        AccountTransaction.customer_id == customer_id,
        AccountTransaction.transaction_type.in_(["payment", "credit"]),
    ).scalar()
    return Decimal(debit or 0) - Decimal(credit or 0)


def customer_json(customer):
    balance = balance_for(customer.id)
    return {
        "id": customer.id,
        "name": f"{customer.first_name} {customer.last_name}",
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "phone": customer.phone,
        "email": customer.email or "",
        "vehicle_count": len(customer.vehicles),
        "balance": money(balance),
        "balance_status": "debt" if balance > 0 else "credit" if balance < 0 else "clear",
    }


def transaction_json(transaction):
    return {
        "id": transaction.id,
        "customer_id": transaction.customer_id,
        "sale_id": transaction.sale_id,
        "vehicle_job_id": transaction.vehicle_job_id,
        "transaction_type": transaction.transaction_type,
        "amount": money(transaction.amount),
        "description": transaction.description or "",
        "created_at": transaction.created_at.isoformat(),
    }


def error(message, status=400):
    return jsonify({"error": message}), status


@accounts_bp.get("/summary")
def summary():
    customers = Customer.query.all()
    balances = [balance_for(customer.id) for customer in customers]
    total_debt = sum((b for b in balances if b > 0), Decimal("0"))
    total_credit = sum((-b for b in balances if b < 0), Decimal("0"))
    customers_with_debt = sum(1 for b in balances if b > 0)
    return jsonify({
        "customer_count": len(customers),
        "customers_with_debt": customers_with_debt,
        "total_debt": money(total_debt),
        "total_credit": money(total_credit),
        "net_balance": money(total_debt - total_credit),
    })


@accounts_bp.get("/customers")
def customers_list():
    search = (request.args.get("search") or "").strip()
    query = Customer.query.order_by(Customer.first_name.asc(), Customer.last_name.asc())
    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            Customer.first_name.ilike(like),
            Customer.last_name.ilike(like),
            Customer.phone.ilike(like),
        ))
    return jsonify([customer_json(customer) for customer in query.all()])


@accounts_bp.get("/customers/<int:customer_id>")
def customer_detail(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return error("Müşteri bulunamadı.", 404)

    transactions = AccountTransaction.query.filter_by(customer_id=customer_id).order_by(
        AccountTransaction.created_at.desc(), AccountTransaction.id.desc()
    ).limit(100).all()
    sales = Sale.query.filter_by(customer_id=customer_id, status="completed").order_by(
        Sale.created_at.desc()
    ).limit(30).all()

    return jsonify({
        "customer": customer_json(customer),
        "transactions": [transaction_json(item) for item in transactions],
        "sales": [{
            "id": sale.id,
            "total_amount": money(sale.total_amount),
            "payment_status": sale.payment_status,
            "payment_method": sale.payment_method,
            "created_at": sale.created_at.isoformat(),
        } for sale in sales],
    })


@accounts_bp.get("/transactions")
def transactions_list():
    limit = min(max(int(request.args.get("limit", 50)), 1), 200)
    query = AccountTransaction.query.order_by(
        AccountTransaction.created_at.desc(), AccountTransaction.id.desc()
    )
    customer_id = request.args.get("customer_id")
    if customer_id:
        try:
            query = query.filter(AccountTransaction.customer_id == int(customer_id))
        except ValueError:
            return error("Geçersiz müşteri.")
    return jsonify([transaction_json(item) for item in query.limit(limit).all()])


@accounts_bp.post("/customers/<int:customer_id>/payments")
def receive_payment(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return error("Müşteri bulunamadı.", 404)

    data = request.get_json() or {}
    try:
        amount = Decimal(str(data.get("amount", 0)))
    except (InvalidOperation, ValueError, TypeError):
        return error("Geçerli bir ödeme tutarı girin.")

    if amount <= 0:
        return error("Ödeme tutarı sıfırdan büyük olmalıdır.")

    method = data.get("payment_method") or "cash"
    if method not in PAYMENT_METHODS:
        return error("Geçersiz ödeme yöntemi.")

    current_balance = balance_for(customer_id)
    if current_balance <= 0:
        return error("Bu müşterinin ödenmemiş borcu bulunmuyor.")
    if amount > current_balance:
        return error(f"Ödeme mevcut borçtan fazla olamaz. Mevcut borç: {current_balance:.2f} TL.")

    note = (data.get("description") or "").strip()
    description = f"Cari ödeme - {PAYMENT_METHODS[method]}"
    if note:
        description += f" - {note}"

    try:
        transaction = AccountTransaction(
            customer_id=customer.id,
            transaction_type="payment",
            amount=amount,
            description=description,
        )
        db.session.add(transaction)
        db.session.commit()
        return jsonify({
            "transaction": transaction_json(transaction),
            "new_balance": money(balance_for(customer_id)),
        }), 201
    except SQLAlchemyError:
        db.session.rollback()
        return error("Ödeme kaydedilirken veritabanı hatası oluştu.", 500)
