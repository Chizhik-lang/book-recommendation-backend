from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def user_to_response(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "source": user.source
    }


@router.post("/login")
def login_user(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь с таким email не найден"
        )

    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Неверный пароль"
        )

    return {
        "message": "Авторизация выполнена успешно",
        "user": user_to_response(user)
    }