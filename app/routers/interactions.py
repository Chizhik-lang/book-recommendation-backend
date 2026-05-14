from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Interaction, Book


router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)


class InteractionUpdate(BaseModel):
    rating: int | None = None
    is_read: bool | None = None
    review_text: str | None = None
    started_at: str | None = None
    read_at: str | None = None
    source: str | None = None


@router.get("/{user_id}")
def get_user_interactions(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    interactions = (
        db.query(Interaction, Book)
        .join(Book, Interaction.book_id == Book.id)
        .filter(Interaction.user_id == user_id)
        .limit(limit)
        .all()
    )

    result = []

    for interaction, book in interactions:
        result.append({
            "interaction_id": interaction.id,
            "user_id": interaction.user_id,
            "book_id": interaction.book_id,
            "is_read": interaction.is_read,
            "rating": interaction.rating,
            "review_text": interaction.review_text,
            "book": {
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "average_rating": book.average_rating
            }
        })

    return result


@router.post("/{user_id}/{book_id}")
def add_interaction(
    user_id: str,
    book_id: str,
    rating: int = Query(5, ge=1, le=5),
    is_read: bool = True,
    review_text: str | None = None,
    db: Session = Depends(get_db)
):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    interaction = Interaction(
        review_id=f"api_review_{user_id}_{book_id}",
        user_id=user_id,
        book_id=book_id,
        is_read=is_read,
        rating=rating,
        review_text=review_text,
        source="added_from_api"
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "message": "Взаимодействие пользователя с книгой добавлено",
        "interaction": interaction
    }


@router.put("/{interaction_id}")
def update_interaction(
    interaction_id: int,
    interaction_data: InteractionUpdate,
    db: Session = Depends(get_db)
):
    interaction = (
        db.query(Interaction)
        .filter(Interaction.id == interaction_id)
        .first()
    )

    if not interaction:
        raise HTTPException(status_code=404, detail="Взаимодействие не найдено")

    update_data = interaction_data.dict(exclude_unset=True)

    if "rating" in update_data:
        if update_data["rating"] < 1 or update_data["rating"] > 5:
            raise HTTPException(
                status_code=400,
                detail="Оценка должна быть от 1 до 5"
            )

    for field, value in update_data.items():
        setattr(interaction, field, value)

    db.commit()
    db.refresh(interaction)

    return {
        "message": "Взаимодействие успешно обновлено",
        "interaction": interaction
    }


@router.delete("/{interaction_id}")
def delete_interaction(
    interaction_id: int,
    db: Session = Depends(get_db)
):
    interaction = (
        db.query(Interaction)
        .filter(Interaction.id == interaction_id)
        .first()
    )

    if not interaction:
        raise HTTPException(status_code=404, detail="Взаимодействие не найдено")

    db.delete(interaction)
    db.commit()

    return {
        "message": "Взаимодействие удалено",
        "interaction_id": interaction_id
    }