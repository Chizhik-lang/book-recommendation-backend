from sqlalchemy import Column, Integer, String, Float, Boolean, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    source = Column(String, nullable=False)


class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author_id = Column(String)
    author = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    description = Column(Text)
    year = Column(Integer)
    average_rating = Column(Float)
    ratings_count = Column(Integer)
    read_count = Column(Integer)
    review_count = Column(Integer)
    goodreads_url = Column(String)
    cover_url = Column(String)
    metadata_source = Column(String)
    metadata_verified = Column(Boolean)


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    book_id = Column(String, nullable=False)
    is_read = Column(Boolean)
    rating = Column(Integer)
    review_text = Column(Text)
    date_added = Column(String)
    date_updated = Column(String)
    started_at = Column(String)
    read_at = Column(String)
    source = Column(String)


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    book_id = Column(String, nullable=False)
    source = Column(String)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    weight = Column(Integer)
    source = Column(String)