from functools import wraps

from flask import abort, g, redirect, session, url_for

from app.models import User


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    if getattr(g, "current_user_obj", None) and g.current_user_obj.user_id == user_id:
        return g.current_user_obj
    user = User.query.get(user_id)
    if user is None:
        session.pop("user_id", None)
        session.pop("role", None)
        g.current_user_obj = None
        return None
    g.current_user_obj = user
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def roles_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = get_current_user()
            if user is None:
                return redirect(url_for("auth.login"))
            if user.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def can_manage_customers(user):
    return user and user.role in {"ADMIN", "MANAGER", "EMPLOYEE"}


def can_delete_customers(user):
    return user and user.role in {"ADMIN", "MANAGER"}


def can_manage_users(user):
    return user and user.role == "ADMIN"


def can_view_audit_logs(user):
    return user and user.role in {"ADMIN", "MANAGER"}
