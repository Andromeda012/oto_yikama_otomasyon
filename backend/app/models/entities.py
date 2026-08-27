from datetime import datetime
from app.extensions import db


class Customer(db.Model):
    __tablename__ = "customers"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False, index=True)
    email = db.Column(db.String(150))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    vehicles = db.relationship("Vehicle", back_populates="customer", cascade="all, delete-orphan")


class Vehicle(db.Model):
    __tablename__ = "vehicles"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    plate = db.Column(db.String(20), nullable=False, unique=True, index=True)
    brand = db.Column(db.String(80))
    model = db.Column(db.String(80))
    year = db.Column(db.Integer)
    color = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer = db.relationship("Customer", back_populates="vehicles")


class Service(db.Model):
    __tablename__ = "services"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Staff(db.Model):
    __tablename__ = "staff"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30))
    role = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="scheduled", index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    customer = db.relationship("Customer")
    vehicle = db.relationship("Vehicle")
    services = db.relationship("AppointmentService", back_populates="appointment", cascade="all, delete-orphan")


class AppointmentService(db.Model):
    __tablename__ = "appointment_services"
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), primary_key=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    appointment = db.relationship("Appointment", back_populates="services")
    service = db.relationship("Service")


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(80), unique=True)
    unit = db.Column(db.String(30), nullable=False, default="adet")
    purchase_price = db.Column(db.Numeric(10, 2), default=0)
    sale_price = db.Column(db.Numeric(10, 2), default=0)
    stock_quantity = db.Column(db.Numeric(12, 3), default=0)
    min_stock_level = db.Column(db.Numeric(12, 3), default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"))
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="completed")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class AccountTransaction(db.Model):
    __tablename__ = "account_transactions"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    transaction_type = db.Column(db.String(30), nullable=False)  # debit / credit / payment
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
