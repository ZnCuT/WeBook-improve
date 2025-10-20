"""
Create a user in the WeBook Flask app.
Usage: python scripts/create_user.py email password

It will import the app and create a user with the provided email/password.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # 延迟导入，以便脚本在导入时不会因为app的导入而静默失败
    from app import app, db, User
except Exception as e:
    print("Failed to import app module:", e)
    raise


def create_user(email, password):
    try:
        with app.app_context():
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"User {email} already exists.")
                return
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Created user {email}")
    except Exception as e:
        print('Error creating user:', e)
        raise


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python scripts/create_user.py email password")
        sys.exit(1)
    create_user(sys.argv[1], sys.argv[2])
