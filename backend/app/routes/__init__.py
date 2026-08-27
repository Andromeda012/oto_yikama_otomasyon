def register_blueprints(app):
    from app.routes.health import health_bp
    from app.routes.pages import pages_bp
    from app.routes.appointments import appointments_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(appointments_bp)
