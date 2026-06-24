import csv
import os

from app import create_app
from app.encryption import decrypt_value
from app.models import CustomerData, User


def main():
    app = create_app()
    with app.app_context():
        key = app.config.get("ENCRYPTION_KEY")
        rows = CustomerData.query.all()
        out_dir = os.path.join(os.path.dirname(__file__), "report")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "customers_export.csv")
        with open(out_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "customer_id",
                "name",
                "email",
                "phone",
                "address",
                "created_by",
                "creator_username",
                "created_at",
            ])
            for r in rows:
                creator = User.query.get(r.created_by)
                writer.writerow([
                    r.customer_id,
                    decrypt_value(r.encrypted_name, key),
                    decrypt_value(r.encrypted_email, key),
                    decrypt_value(r.encrypted_phone, key),
                    decrypt_value(r.encrypted_address, key),
                    r.created_by,
                    creator.username if creator else "",
                    r.created_at.isoformat() if r.created_at else "",
                ])
        print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
