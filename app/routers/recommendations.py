from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Book, Interaction, Favorite, UserPreference, User


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/{user_id}")
def get_recommendations(
    user_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .all()
    )

    preferred_genres = {
        preference.genre: preference.weight
        for preference in preferences
    }

    user_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == user_id)
        .all()
    )

    interacted_book_ids = {
        interaction.book_id
        for interaction in user_interactions
    }

    favorite_book_ids = {
        favorite.book_id
        for favorite in db.query(Favorite).filter(Favorite.user_id == user_id).all()
    }

    # Дополнительно усиливаем жанры книг, которые пользователь оценил высоко
    for interaction in user_interactions:
        if interaction.rating and interaction.rating >= 4:
            book = db.query(Book).filter(Book.id == interaction.book_id).first()
            if book:
                preferred_genres[book.genre] = preferred_genres.get(book.genre, 0) + interaction.rating

    # Дополнительно усиливаем жанры книг из избранного
    for book_id in favorite_book_ids:
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            preferred_genres[book.genre] = preferred_genres.get(book.genre, 0) + 3

    if not preferred_genres:
        books = (
            db.query(Book)
            .order_by(Book.average_rating.desc())
            .limit(limit)
            .all()
        )

        return {
            "user_id": user_id,
            "recommendation_type": "popular_books",
            "message": "У пользователя пока нет предпочтений, поэтому показаны популярные книги",
            "recommendations": books
        }

    candidate_books = (
        db.query(Book)
        .filter(~Book.id.in_(interacted_book_ids))
        .all()
    )

    recommendations = []

    for book in candidate_books:
        genre_weight = preferred_genres.get(book.genre, 0)

        if genre_weight <= 0:
            continue

        rating_score = book.average_rating if book.average_rating else 0
        popularity_score = 0

        if book.ratings_count:
            popularity_score += min(book.ratings_count / 1000, 2)

        score = genre_weight * 2 + rating_score + popularity_score

        recommendations.append({
            "book_id": book.id,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "description": book.description,
            "average_rating": book.average_rating,
            "score": round(score, 2),
            "reason": f"Рекомендовано, потому что пользователь интересуется жанром {book.genre}"
        })

    recommendations = sorted(
        recommendations,
        key=lambda item: item["score"],
        reverse=True
    )

    return {
        "user_id": user_id,
        "recommendation_type": "hybrid_content_based",
        "preferred_genres": preferred_genres,
        "recommendations": recommendations[:limit]
    }


@router.get("/{user_id}/stats")
def get_recommendation_stats(user_id: str, db: Session = Depends(get_db)):
    total_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == user_id)
        .count()
    )

    total_favorites = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id)
        .count()
    )

    preferences = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user_id)
        .order_by(UserPreference.weight.desc())
        .all()
    )

    avg_rating = (
        db.query(func.avg(Interaction.rating))
        .filter(Interaction.user_id == user_id)
        .scalar()
    )

    return {
        "user_id": user_id,
        "total_interactions": total_interactions,
        "total_favorites": total_favorites,
        "average_user_rating": round(avg_rating, 2) if avg_rating else None,
        "preferences": preferences
    }