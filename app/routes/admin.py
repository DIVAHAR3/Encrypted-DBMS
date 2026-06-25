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
    users = User.query.order_by(User.created_at.desc()).all()
    if request.method == "POST":
        user_id_raw = request.form.get("user_id", "")
        if not user_id_raw.isdigit():
            abort(400)
        user_id = int(user_id_raw)
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

    return render_template(
        "users.html",
        users=users,
        user_count=len(users),
        admin_count=sum(1 for user in users if user.role == "ADMIN"),
        manager_count=sum(1 for user in users if user.role == "MANAGER"),
        employee_count=sum(1 for user in users if user.role == "EMPLOYEE"),
    )


@admin_bp.route("/audit-logs")
@login_required
@roles_required("ADMIN", "MANAGER")
def audit_logs():
    logs = AuditLog.query.order_by(AuditLog.log_time.desc()).limit(200).all()
    failed_logins = FailedLogin.query.order_by(FailedLogin.attempt_time.desc()).limit(50).all()
    return render_template("audit_logs.html", logs=logs, failed_logins=failed_logins)


@admin_bp.route("/manager/add-admin", methods=["GET", "POST"])
@login_required
@roles_required("MANAGER")
def manager_add_admin():
    """Allow managers to create admin users.

    This endpoint is intentionally limited: managers can only create new users
    with the ADMIN role (or update an existing user to ADMIN). They cannot
    change other users' roles or view the full user management interface.
    """
    current_user = get_current_user()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("add_admin.html")
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            # If user exists, upgrade role to ADMIN and reset password
            from extensions import bcrypt as _bcrypt

            existing.password_hash = _bcrypt.generate_password_hash(password).decode("utf-8")
            existing.role = "ADMIN"
            log_action(current_user.user_id, "CREATE_ADMIN", f"Upgraded existing user {username} to ADMIN")
            db.session.commit()
            flash("Existing user upgraded to ADMIN.", "success")
            return redirect(url_for("admin.audit_logs"))
        # create new admin user
        from extensions import bcrypt as _bcrypt

        pw_hash = _bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password_hash=pw_hash, role="ADMIN")
        db.session.add(new_user)
        log_action(current_user.user_id, "CREATE_ADMIN", f"Created new admin {username}")
        db.session.commit()
        flash("New admin user created.", "success")
        return redirect(url_for("admin.audit_logs"))

    return render_template("add_admin.html")
