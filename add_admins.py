from app import create_app
from extensions import bcrypt, db
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        usernames = ["test1", "test2", "test3", "test4", "test5"]
        password = "123456789"
        for name in usernames:
            user = User.query.filter_by(username=name).first()
            pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            if user:
                user.email = f"{name}@example.com"
                user.password_hash = pw_hash
                user.role = "ADMIN"
            else:
                user = User(username=name, email=f"{name}@example.com", password_hash=pw_hash, role="ADMIN")
                db.session.add(user)
        db.session.commit()
        print(f"Created/updated {len(usernames)} admin users with provided password")


if __name__ == "__main__":
    main()
