from app import create_app
from extensions import bcrypt, db
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        username = "admin"
        email = "admin@example.com"
        password = "123456789"
        
        user = User.query.filter_by(username=username).first()
        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        
        if user:
            user.email = email
            user.password_hash = pw_hash
            user.role = "MANAGER"
            print(f"Updated existing user '{username}' to MANAGER role")
        else:
            user = User(username=username, email=email, password_hash=pw_hash, role="MANAGER")
            db.session.add(user)
            print(f"Created new manager user '{username}'")
        
        db.session.commit()
        print(f"Manager user ready: username='{username}', password='123456789'")


if __name__ == "__main__":
    main()
