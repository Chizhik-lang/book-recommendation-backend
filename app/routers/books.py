from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.database import get_db
from app.models import Book


router = APIRouter(
    prefix="/books",
    tags=["Books"]
)


@router.get("/")
def get_books(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    genre: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Book)

    if genre:
        query = query.filter(Book.genre == genre)

    books = (
        query
        .order_by(Book.average_rating.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return books


@router.get("/search")
def search_books(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    books = (
        db.query(Book)
        .filter(
            or_(
                Book.title.ilike(f"%{q}%"),
                Book.author.ilike(f"%{q}%"),
                Book.genre.ilike(f"%{q}%")
            )
        )
        .order_by(Book.average_rating.desc())
        .limit(limit)
        .all()
    )

    return {
        "query": q,
        "count": len(books),
        "results": books
    }


@router.get("/top")
def get_top_books(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    books = (
        db.query(Book)
        .order_by(Book.average_rating.desc(), Book.ratings_count.desc())
        .limit(limit)
        .all()
    )

    return {
        "message": "Топ книг по среднему рейтингу",
        "count": len(books),
        "books": books
    }


@router.get("/genres/list")
def get_genres(db: Session = Depends(get_db)):
    genres = db.query(Book.genre).distinct().order_by(Book.genre).all()
    return [genre[0] for genre in genres]


@router.get("/genre/{genre_name}")
def get_books_by_genre(
    genre_name: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    books = (
        db.query(Book)
        .filter(Book.genre == genre_name)
        .order_by(Book.average_rating.desc())
        .limit(limit)
        .all()
    )

    return {
        "genre": genre_name,
        "count": len(books),
        "books": books
    }


@router.get("/stats/summary")
def get_books_stats(db: Session = Depends(get_db)):
    total_books = db.query(Book).count()
    total_genres = db.query(Book.genre).distinct().count()
    avg_rating = db.query(func.avg(Book.average_rating)).scalar()

    books_by_genre = (
        db.query(Book.genre, func.count(Book.id))
        .group_by(Book.genre)
        .order_by(func.count(Book.id).desc())
        .all()
    )

    return {
        "total_books": total_books,
        "total_genres": total_genres,
        "average_catalog_rating": round(avg_rating, 2) if avg_rating else None,
        "books_by_genre": [
            {
                "genre": genre,
                "count": count
            }
            for genre, count in books_by_genre
        ]
    }


@router.get("/{book_id}")
def get_book(book_id: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    return book