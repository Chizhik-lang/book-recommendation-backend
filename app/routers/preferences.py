from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserPreference


router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"]
)


@router.get("/{user_id}")
def get_user_preferences(user_id: str, db: Session = Depends(get_db)):
    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .order_by(UserPreference.weight.desc())
        .all()
    )

    return preferences


@router.post("/{user_id}")
def add_user_preference(
    user_id: str,
    genre: str,
    weight: int = 5,
    db: Session = Depends(get_db)
):
    preference = UserPreference(
        user_id=user_id,
        genre=genre,
        weight=weight,
        source="added_from_api"
    )

    db.add(preference)
    db.commit()
    db.refresh(preference)

    return {
        "message": "Жанровое предпочтение добавлено",
        "preference": preference
    }