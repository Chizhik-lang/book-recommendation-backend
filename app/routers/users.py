from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


class UserCreate(BaseModel):
    id: str
    username: str
    email: EmailStr
    password_hash: str = "demo_password_hash"
    source: str = "created_from_api"


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password_hash: str | None = None


@router.get("/")
def get_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    users = (
        db.query(User)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return users


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user


@router.post("/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user_data.id).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким id уже существует"
        )

    existing_email = db.query(User).filter(User.email == user_data.email).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже существует"
        )

    new_user = User(
        id=user_data.id,
        username=user_data.username,
        email=user_data.email,
        password_hash=user_data.password_hash,
        source=user_data.source
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Пользователь успешно создан",
        "user": new_user
    }


@router.put("/{user_id}")
def update_user(
    user_id: str,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    update_data = user_data.dict(exclude_unset=True)

    if "email" in update_data:
        existing_email = (
            db.query(User)
            .filter(User.email == update_data["email"], User.id != user_id)
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Пользователь с таким email уже существует"
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return {
        "message": "Данные пользователя успешно обновлены",
        "user": user
    }


@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    db.delete(user)
    db.commit()

    return {
        "message": "Пользователь успешно удалён",
        "user_id": user_id
    }