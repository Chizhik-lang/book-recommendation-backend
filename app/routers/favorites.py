from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Favorite, Book


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"]
)


class FavoriteUpdate(BaseModel):
    book_id: str | None = None
    source: str | None = None


@router.get("/{user_id}")
def get_user_favorites(user_id: str, db: Session = Depends(get_db)):
    favorites = (
        db.query(Favorite, Book)
        .join(Book, Favorite.book_id == Book.id)
        .filter(Favorite.user_id == user_id)
        .all()
    )

    result = []

    for favorite, book in favorites:
        result.append({
            "favorite_id": favorite.id,
            "user_id": favorite.user_id,
            "book": {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "average_rating": book.average_rating,
                "description": book.description
            }
        })

    return result


@router.post("/{user_id}/{book_id}")
def add_favorite(user_id: str, book_id: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    existing = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.book_id == book_id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Книга уже добавлена в избранное")

    favorite = Favorite(
        user_id=user_id,
        book_id=book_id,
        source="added_from_api"
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return {
        "message": "Книга добавлена в избранное",
        "favorite_id": favorite.id,
        "user_id": user_id,
        "book_id": book_id
    }


@router.put("/{favorite_id}")
def update_favorite(
    favorite_id: int,
    favorite_data: FavoriteUpdate,
    db: Session = Depends(get_db)
):
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()

    if not favorite:
        raise HTTPException(status_code=404, detail="Запись в избранном не найдена")

    update_data = favorite_data.dict(exclude_unset=True)

    if "book_id" in update_data:
        book = db.query(Book).filter(Book.id == update_data["book_id"]).first()

        if not book:
            raise HTTPException(status_code=404, detail="Новая книга не найдена")

        existing = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == favorite.user_id,
                Favorite.book_id == update_data["book_id"],
                Favorite.id != favorite_id
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Эта книга уже есть в избранном у пользователя"
            )

    for field, value in update_data.items():
        setattr(favorite, field, value)

    db.commit()
    db.refresh(favorite)

    return {
        "message": "Запись в избранном успешно обновлена",
        "favorite": favorite
    }


@router.delete("/{user_id}/{book_id}")
def delete_favorite(user_id: str, book_id: str, db: Session = Depends(get_db)):
    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.book_id == book_id)
        .first()
    )

    if not favorite:
        raise HTTPException(status_code=404, detail="Запись в избранном не найдена")

    db.delete(favorite)
    db.commit()

    return {
        "message": "Книга удалена из избранного",
        "user_id": user_id,
        "book_id": book_id
    }
