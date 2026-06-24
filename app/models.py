from datetime import datetime

from sqlalchemy import Enum, func

from extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        Enum("ADMIN", "MANAGER", "EMPLOYEE", name="user_role"),
        nullable=False,
        default="EMPLOYEE",
    )
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())

    customers = db.relationship("CustomerData", backref="creator", lazy=True)
    audit_logs = db.relationship("AuditLog", backref="user", lazy=True)


class CustomerData(db.Model):
    __tablename__ = "customer_data"

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    encrypted_name = db.Column(db.Text, nullable=False)
    encrypted_email = db.Column(db.Text, nullable=False)
    encrypted_phone = db.Column(db.Text, nullable=False)
    encrypted_address = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    log_time = db.Column(db.DateTime, nullable=False, server_default=func.now(), index=True)


class FailedLogin(db.Model):
    __tablename__ = "failed_logins"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, index=True)
    ip_address = db.Column(db.String(50), nullable=False)
    attempt_time = db.Column(db.DateTime, nullable=False, server_default=func.now(), index=True)
