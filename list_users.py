from app import create_app
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        users = User.query.order_by(User.user_id).all()
        if not users:
            print('No users found')
            return
        for u in users:
            print(u.user_id, u.username, u.email, u.role)


if __name__ == '__main__':
    main()
