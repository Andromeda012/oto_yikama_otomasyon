def register_blueprints(app):
    from app.routes.health import health_bp
    from app.routes.appointments import appointments_bp
    from app.routes.definitions import definitions_bp
    from app.routes.vehicle_tracking import vehicle_tracking_bp
    from app.routes.market import market_bp
    from app.routes.accounts import accounts_bp
    from app.routes.company import company_bp
    from app.routes.settings import settings_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.statistics import statistics_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(definitions_bp)
    app.register_blueprint(vehicle_tracking_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(accounts_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(statistics_bp)
