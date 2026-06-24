from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import AuditLog, FailedLogin, User
from app.permissions import get_current_user, login_required, roles_required
from app.services.audit import log_action
from extensions import db


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN")
def users():
    current_user = get_current_user()
    if request.method == "POST":
        user_id = int(request.form.get("user_id", 0))
        role = request.form.get("role", "EMPLOYEE")
        if role not in {"ADMIN", "MANAGER", "EMPLOYEE"}:
            abort(400)
        target_user = User.query.get_or_404(user_id)
        if target_user.user_id == current_user.user_id:
            flash("You cannot change your own role.", "warning")
        else:
            target_user.role = role
            log_action(
                current_user.user_id,
                "UPDATE_ROLE",
                f"Changed role for {target_user.username} to {role}",
            )
            db.session.commit()
            flash("User role updated.", "success")
        return redirect(url_for("admin.users"))

    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("users.html", users=users)


@admin_bp.route("/audit-logs")
@login_required
@roles_required("ADMIN", "MANAGER")
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.log_time.desc()).limit(200).all()
    failed_logins = FailedLogin.query.order_by(FailedLogin.attempt_time.desc()).limit(50).all()
    return render_template("audit_logs.html", logs=logs, failed_logins=failed_logins)
