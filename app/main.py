from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    books,
    users,
    favorites,
    preferences,
    interactions,
    recommendations,
    stats
)


app = FastAPI(
    title="Book Recommendation Backend",
    description="Backend веб-приложения для интеллектуального подбора книг",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(books.router)
app.include_router(users.router)
app.include_router(favorites.router)
app.include_router(preferences.router)
app.include_router(interactions.router)
app.include_router(recommendations.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {
        "message": "Backend для подбора книг работает",
        "available_modules": [
            "books",
            "users",
            "favorites",
            "preferences",
            "interactions",
            "recommendations"
        ]
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }