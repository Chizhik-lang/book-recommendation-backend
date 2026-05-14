from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Book, Interaction, Favorite, UserPreference


router = APIRouter(
    prefix="/stats",
    tags=["Project Statistics"]
)


@router.get("/")
def get_project_stats(db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_books = db.query(Book).count()
    total_interactions = db.query(Interaction).count()
    total_favorites = db.query(Favorite).count()
    total_preferences = db.query(UserPreference).count()
    total_genres = db.query(Book.genre).distinct().count()

    average_book_rating = db.query(func.avg(Book.average_rating)).scalar()
    average_user_rating = db.query(func.avg(Interaction.rating)).scalar()

    return {
        "total_users": total_users,
        "total_books": total_books,
        "total_interactions": total_interactions,
        "total_favorites": total_favorites,
        "total_preferences": total_preferences,
        "total_genres": total_genres,
        "average_book_rating": round(average_book_rating, 2) if average_book_rating else None,
        "average_user_rating": round(average_user_rating, 2) if average_user_rating else None,
        "database_description": "База данных для веб-приложения интеллектуального подбора книг"
    }