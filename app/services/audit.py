from sqlalchemy import text

from extensions import db
from app.models import AuditLog, FailedLogin


def log_action(user_id, action, description):
    db.session.add(AuditLog(user_id=user_id, action=action, description=description))


def log_failed_login(username, ip_address):
    db.session.add(FailedLogin(username=username, ip_address=ip_address))


def set_mysql_user_context(user_id):
    if db.engine.dialect.name != "mysql":
        return

    db.session.execute(
        text("SET @app_user_id = :user_id"),
        {"user_id": user_id or 0},
    )
