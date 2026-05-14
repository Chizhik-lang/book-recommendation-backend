from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def set_unique_passwords():
    db = SessionLocal()

    try:
        users = db.query(User).order_by(User.id).all()

        for user in users:
            plain_password = f"pass_{user.id}"
            user.password_hash = hash_password(plain_password)

        db.commit()

        print("Уникальные пароли установлены:")
        for user in users:
            print(f"{user.id} -> pass_{user.id}")

    finally:
        db.close()


if __name__ == "__main__":
    set_unique_passwords()