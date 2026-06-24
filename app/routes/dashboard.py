from datetime import datetime, timedelta

from flask import render_template

from app.models import AuditLog, CustomerData, FailedLogin, User
from app.permissions import get_current_user, login_required, roles_required
from app.services.audit import log_action
from extensions import db

from flask import Blueprint


dashboard_bp = Blueprint("dashboard", __name__)


def _portal_context():
    user = get_current_user()
    total_users = User.query.count()
    total_customers = CustomerData.query.count()
    failed_login_count = FailedLogin.query.filter(
        FailedLogin.attempt_time >= datetime.utcnow() - timedelta(days=1)
    ).count()
    recent_activities = AuditLog.query.order_by(AuditLog.log_time.desc()).limit(8).all()

    if user and user.role == "ADMIN":
        portal_label = "ADMIN Portal"
        portal_heading = "Operate users, audit logs, and customer access from one control center."
        portal_subheading = (
            "This portal is the privileged entry point for administrators. Use it to manage accounts, review logs, "
            "and supervise encrypted customer data."
        )
        portal_actions = [
            {
                "title": "User Management",
                "description": "Review accounts and promote or restrict access.",
                "href": "/users",
                "button": "Open Admin Tools",
            },
            {
                "title": "Security Audit",
                "description": "Track recent actions, failed logins, and system activity.",
                "href": "/audit-logs",
                "button": "View Audit Logs",
            },
            {
                "title": "Customer Console",
                "description": "Search, add, edit, and delete encrypted customer records.",
                "href": "/customers",
                "button": "Open Customers",
            },
        ]
    else:
        portal_label = "MANAGER Portal"
        portal_heading = "Monitor activity, review logs, and manage encrypted customer operations."
        portal_subheading = (
            "This portal is optimized for managers. It surfaces security alerts, customer operations, and audit "
            "visibility without exposing admin-only controls."
        )
        portal_actions = [
            {
                "title": "Security Audit",
                "description": "Review recent actions, failed logins, and suspicious activity.",
                "href": "/audit-logs",
                "button": "Open Audit Logs",
            },
            {
                "title": "Customer Console",
                "description": "Search, add, and edit encrypted customer records.",
                "href": "/customers",
                "button": "Open Customers",
            },
            {
                "title": "Security Dashboard",
                "description": "Check totals, alerts, and operational health at a glance.",
                "href": "/dashboard",
                "button": "Open Dashboard",
            },
        ]

    return {
        "portal_label": portal_label,
        "portal_heading": portal_heading,
        "portal_subheading": portal_subheading,
        "total_users": total_users,
        "total_customers": total_customers,
        "failed_login_count": failed_login_count,
        "recent_activities": recent_activities,
        "portal_actions": portal_actions,
    }


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    total_users = User.query.count()
    total_customers = CustomerData.query.count()
    failed_login_count = FailedLogin.query.filter(
        FailedLogin.attempt_time >= datetime.utcnow() - timedelta(days=1)
    ).count()
    recent_activities = (
        AuditLog.query.order_by(AuditLog.log_time.desc()).limit(10).all()
    )
    recent_failed_logins = (
        FailedLogin.query.order_by(FailedLogin.attempt_time.desc()).limit(5).all()
    )

    security_alerts = []
    if failed_login_count:
        security_alerts.append(
            f"{failed_login_count} failed login attempt(s) detected in the last 24 hours."
        )
    if total_customers == 0:
        security_alerts.append("No encrypted customer records stored yet.")

    log_action(user.user_id, "VIEW_DASHBOARD", f"{user.username} opened the security dashboard")
    db.session.commit()

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_customers=total_customers,
        failed_login_count=failed_login_count,
        recent_activities=recent_activities,
        recent_failed_logins=recent_failed_logins,
        security_alerts=security_alerts,
    )


@dashboard_bp.route("/portal")
@login_required
@roles_required("ADMIN", "MANAGER")
def portal():
    return render_template("portal.html", **_portal_context())


@dashboard_bp.route("/manager")
@login_required
@roles_required("ADMIN", "MANAGER")
def manager_portal():
    return render_template("portal.html", **_portal_context())
