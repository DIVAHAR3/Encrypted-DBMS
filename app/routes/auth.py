from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models import User
from app.permissions import get_current_user, login_required
from app.services.audit import log_action, log_failed_login
from extensions import bcrypt, db


auth_bp = Blueprint("auth", __name__)


def _post_login_redirect(role):
    if role in {"ADMIN", "MANAGER"}:
        return redirect(url_for("dashboard.portal"))
    return redirect(url_for("dashboard.dashboard"))


@auth_bp.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "warning")
            return render_template("register.html")

        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=password_hash, role="EMPLOYEE")
        db.session.add(user)
        db.session.flush()
        log_action(user.user_id, "REGISTER", f"User {username} created an account")
        db.session.commit()

        session["user_id"] = user.user_id
        session["role"] = user.role
        session.permanent = True
        flash("Registration successful.", "success")
        return _post_login_redirect(user.role)

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter((User.username == username) | (User.email == username.lower())).first()

        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            log_failed_login(username=username, ip_address=request.remote_addr or "unknown")
            log_action(
                None,
                "LOGIN_FAILED",
                f"Failed login attempt for {username} from {request.remote_addr or 'unknown'}",
            )
            db.session.commit()
            flash("Invalid credentials.", "danger")
            return render_template("login.html")

        session["user_id"] = user.user_id
        session["role"] = user.role
        session.permanent = True
        log_action(user.user_id, "LOGIN", f"User {user.username} logged in successfully")
        db.session.commit()
        flash("Logged in successfully.", "success")
        return _post_login_redirect(user.role)

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    user = get_current_user()
    if user:
        log_action(user.user_id, "LOGOUT", f"User {user.username} logged out")
        db.session.commit()
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
@login_required
def profile():
    user = get_current_user()
    return render_template("profile.html", profile_user=user)
