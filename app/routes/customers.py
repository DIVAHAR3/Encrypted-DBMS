from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from app.encryption import decrypt_value, encrypt_value
from app.models import CustomerData, User
from app.permissions import get_current_user, login_required, roles_required
from app.services.audit import log_action, set_mysql_user_context
from extensions import db


customers_bp = Blueprint("customers", __name__)


def _customer_to_dict(customer):
    key = current_app.config["ENCRYPTION_KEY"]
    return {
        "customer_id": customer.customer_id,
        "name": decrypt_value(customer.encrypted_name, key),
        "email": decrypt_value(customer.encrypted_email, key),
        "phone": decrypt_value(customer.encrypted_phone, key),
        "address": decrypt_value(customer.encrypted_address, key),
        "created_by": customer.created_by,
        "created_at": customer.created_at,
    }


def _search_customer_records(search_text: str):
    customers = CustomerData.query.order_by(CustomerData.created_at.desc()).all()
    results = []
    normalized_search = search_text.strip().lower()

    for customer in customers:
        customer_dict = _customer_to_dict(customer)
        if normalized_search:
            haystack = " ".join(
                [
                    customer_dict["name"],
                    customer_dict["email"],
                    customer_dict["phone"],
                    customer_dict["address"],
                    str(customer_dict["created_by"]),
                ]
            ).lower()
            if normalized_search not in haystack:
                continue
        results.append(customer_dict)

    return results


@customers_bp.route("/customers")
@login_required
@roles_required("ADMIN", "MANAGER", "EMPLOYEE")
def customers():
    search_text = request.args.get("q", "")
    customer_rows = _search_customer_records(search_text)
    return render_template("customers.html", customers=customer_rows, search_text=search_text)


@customers_bp.route("/customers/add", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN", "MANAGER", "EMPLOYEE")
def add_customer():
    current_user = get_current_user()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not email or not phone or not address:
            flash("All fields are required.", "danger")
            return render_template("customer_form.html", form_title="Add Customer", customer=None)

        customer = CustomerData(
            encrypted_name=encrypt_value(name, current_app.config["ENCRYPTION_KEY"]),
            encrypted_email=encrypt_value(email, current_app.config["ENCRYPTION_KEY"]),
            encrypted_phone=encrypt_value(phone, current_app.config["ENCRYPTION_KEY"]),
            encrypted_address=encrypt_value(address, current_app.config["ENCRYPTION_KEY"]),
            created_by=current_user.user_id,
        )
        db.session.add(customer)
        db.session.flush()
        set_mysql_user_context(current_user.user_id)
        log_action(current_user.user_id, "CREATE_CUSTOMER", f"Created customer record #{customer.customer_id}")
        db.session.commit()
        flash("Customer created successfully.", "success")
        return redirect(url_for("customers.customers"))

    return render_template("customer_form.html", form_title="Add Customer", customer=None)


@customers_bp.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN", "MANAGER", "EMPLOYEE")
def edit_customer(customer_id):
    current_user = get_current_user()
    customer = CustomerData.query.get_or_404(customer_id)
    customer_data = _customer_to_dict(customer)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not email or not phone or not address:
            flash("All fields are required.", "danger")
            return render_template("customer_form.html", form_title="Edit Customer", customer=customer_data)

        key = current_app.config["ENCRYPTION_KEY"]
        customer.encrypted_name = encrypt_value(name, key)
        customer.encrypted_email = encrypt_value(email, key)
        customer.encrypted_phone = encrypt_value(phone, key)
        customer.encrypted_address = encrypt_value(address, key)
        set_mysql_user_context(current_user.user_id)
        log_action(current_user.user_id, "UPDATE_CUSTOMER", f"Updated customer record #{customer.customer_id}")
        db.session.commit()
        flash("Customer updated successfully.", "success")
        return redirect(url_for("customers.customers"))

    return render_template("customer_form.html", form_title="Edit Customer", customer=customer_data)


@customers_bp.route("/customers/<int:customer_id>/delete", methods=["POST"])
@login_required
@roles_required("ADMIN", "MANAGER")
def delete_customer(customer_id):
    current_user = get_current_user()
    customer = CustomerData.query.get_or_404(customer_id)
    set_mysql_user_context(current_user.user_id)
    log_action(current_user.user_id, "DELETE_CUSTOMER", f"Deleted customer record #{customer.customer_id}")
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted successfully.", "success")
    return redirect(url_for("customers.customers"))
