from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import UserPreference


router = APIRouter(
    prefix="/preferences",
    tags=["Preferences"]
)


class PreferenceUpdate(BaseModel):
    genre: str | None = None
    weight: int | None = None
    source: str | None = None


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
    weight: int = Query(5, ge=1, le=10),
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


@router.put("/{preference_id}")
def update_user_preference(
    preference_id: int,
    preference_data: PreferenceUpdate,
    db: Session = Depends(get_db)
):
    preference = (
        db.query(UserPreference)
        .filter(UserPreference.id == preference_id)
        .first()
    )

    if not preference:
        raise HTTPException(status_code=404, detail="Предпочтение не найдено")

    update_data = preference_data.dict(exclude_unset=True)

    if "weight" in update_data:
        if update_data["weight"] < 1 or update_data["weight"] > 10:
            raise HTTPException(
                status_code=400,
                detail="Вес предпочтения должен быть от 1 до 10"
            )

    for field, value in update_data.items():
        setattr(preference, field, value)

    db.commit()
    db.refresh(preference)

    return {
        "message": "Жанровое предпочтение успешно обновлено",
        "preference": preference
    }


@router.delete("/{preference_id}")
def delete_user_preference(
    preference_id: int,
    db: Session = Depends(get_db)
):
    preference = (
        db.query(UserPreference)
        .filter(UserPreference.id == preference_id)
        .first()
    )

    if not preference:
        raise HTTPException(status_code=404, detail="Предпочтение не найдено")

    db.delete(preference)
    db.commit()

    return {
        "message": "Жанровое предпочтение удалено",
        "preference_id": preference_id
    }