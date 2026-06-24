from flask import Flask, g, session

from config import Config
from extensions import bcrypt, db
from app.models import AuditLog, CustomerData, FailedLogin, User
from app.permissions import get_current_user


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)

    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.customers import customers_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def load_current_user():
        g.current_user = get_current_user()

    @app.context_processor
    def inject_globals():
        return {
            "current_user": getattr(g, "current_user", None),
            "current_role": getattr(g.current_user, "role", None) if getattr(g, "current_user", None) else None,
        }

    @app.shell_context_processor
    def shell_context():
        return {
            "db": db,
            "User": User,
            "CustomerData": CustomerData,
            "AuditLog": AuditLog,
            "FailedLogin": FailedLogin,
        }

    if app.config.get("AUTO_CREATE_TABLES") or app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///"):
        with app.app_context():
            db.create_all()

    return app
