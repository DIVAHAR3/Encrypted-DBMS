from app import create_app
from app.encryption import decrypt_value
from app.models import CustomerData, User


def main():
    app = create_app()
    with app.app_context():
        key = app.config.get("ENCRYPTION_KEY")
        rows = CustomerData.query.limit(100).all()
        if not rows:
            print("No customer rows found.")
            return
        for r in rows:
            creator = User.query.get(r.created_by)
            print(
                r.customer_id,
                decrypt_value(r.encrypted_name, key),
                decrypt_value(r.encrypted_email, key),
                decrypt_value(r.encrypted_phone, key),
                decrypt_value(r.encrypted_address, key),
                f"created_by={r.created_by}",
                f"creator_username={creator.username if creator else None}",
                f"created_at={r.created_at}",
            )


if __name__ == "__main__":
    main()
