from flask import Flask
from flask_cors import CORS
from config.settings import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)
    db.init_app(app)
    CORS(app, origins=app.config.get("CORS_ORIGINS", "*"))

    from app.routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()
        _seed_demo_data()

    return app


def _seed_demo_data():
    from app.models import Customer, Vehicle, Service
    if Service.query.first():
        return
    ahmet = Customer(first_name="Ahmet", last_name="Yılmaz", phone="0532 000 00 01")
    mehmet = Customer(first_name="Mehmet", last_name="Kaya", phone="0532 000 00 02")
    ayse = Customer(first_name="Ayşe", last_name="Demir", phone="0532 000 00 03")
    db.session.add_all([ahmet, mehmet, ayse])
    db.session.flush()
    db.session.add_all([
        Vehicle(customer_id=ahmet.id, plate="34 ABC 123", brand="BMW", model="320i"),
        Vehicle(customer_id=mehmet.id, plate="16 XYZ 456", brand="Audi", model="A4"),
        Vehicle(customer_id=ayse.id, plate="06 DEF 789", brand="Mercedes", model="C200"),
    ])
    db.session.add_all([
        Service(name="Dış Yıkama", price=300, duration_minutes=30),
        Service(name="İç + Dış Yıkama", price=500, duration_minutes=60),
        Service(name="Detaylı Temizlik", price=1500, duration_minutes=120),
        Service(name="Pasta / Cila", price=2000, duration_minutes=150),
        Service(name="İç Yıkama", price=350, duration_minutes=45),
    ])
    db.session.commit()
