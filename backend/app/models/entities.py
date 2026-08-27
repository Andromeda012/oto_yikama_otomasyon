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


class VehicleJob(db.Model):
    __tablename__ = "vehicle_jobs"
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id", ondelete="SET NULL"), unique=True, nullable=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False, index=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id", ondelete="SET NULL"), nullable=True, index=True)
    status = db.Column(db.String(30), nullable=False, default="waiting", index=True)
    priority = db.Column(db.Integer, nullable=False, default=0)
    check_in_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    estimated_end_at = db.Column(db.DateTime)
    ready_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    appointment = db.relationship("Appointment", backref=db.backref("vehicle_job", uselist=False))
    customer = db.relationship("Customer")
    vehicle = db.relationship("Vehicle")
    staff = db.relationship("Staff")
    services = db.relationship("VehicleJobService", back_populates="job", cascade="all, delete-orphan")
    history = db.relationship("VehicleJobStatusHistory", back_populates="job", cascade="all, delete-orphan", order_by="VehicleJobStatusHistory.changed_at")


class VehicleJobService(db.Model):
    __tablename__ = "vehicle_job_services"
    job_id = db.Column(db.Integer, db.ForeignKey("vehicle_jobs.id", ondelete="CASCADE"), primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), primary_key=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    job = db.relationship("VehicleJob", back_populates="services")
    service = db.relationship("Service")


class VehicleJobStatusHistory(db.Model):
    __tablename__ = "vehicle_job_status_history"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("vehicle_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.String(255))
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    job = db.relationship("VehicleJob", back_populates="history")


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
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"))
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.id", ondelete="SET NULL"))
    vehicle_job_id = db.Column(db.Integer, db.ForeignKey("vehicle_jobs.id", ondelete="SET NULL"), unique=True, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    status = db.Column(db.String(30), nullable=False, default="completed")
    payment_status = db.Column(db.String(30), nullable=False, default="unpaid")
    payment_method = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    items = db.relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    vehicle_job = db.relationship("VehicleJob", backref=db.backref("sale", uselist=False))


class SaleItem(db.Model):
    __tablename__ = "sale_items"
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id", ondelete="CASCADE"), nullable=False, index=True)
    line_type = db.Column(db.String(20), nullable=False)  # service / product
    service_id = db.Column(db.Integer, db.ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    sale = db.relationship("Sale", back_populates="items")
    service = db.relationship("Service")
    product = db.relationship("Product")


class AccountTransaction(db.Model):
    __tablename__ = "account_transactions"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"))
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id", ondelete="SET NULL"), index=True)
    vehicle_job_id = db.Column(db.Integer, db.ForeignKey("vehicle_jobs.id", ondelete="SET NULL"), index=True)
    transaction_type = db.Column(db.String(30), nullable=False)  # debit / credit / payment
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)


class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    sale_id = db.Column(db.Integer, db.ForeignKey("sales.id", ondelete="SET NULL"), nullable=True, index=True)
    movement_type = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Numeric(12, 3), nullable=False)
    stock_before = db.Column(db.Numeric(12, 3), nullable=False)
    stock_after = db.Column(db.Numeric(12, 3), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    product = db.relationship("Product")
    sale = db.relationship("Sale")
