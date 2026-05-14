from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


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