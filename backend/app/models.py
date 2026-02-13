"""
SQLAlchemy ORM models for the Wiki Quiz application.
Defines the Quiz and Question tables.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Quiz(Base):
    """
    Represents a generated quiz from a Wikipedia article.
    Stores the article metadata, extracted content, and raw HTML.
    """

    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(2048), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    key_entities = Column(JSON, nullable=False, default=dict)
    sections = Column(JSON, nullable=False, default=list)
    related_topics = Column(JSON, nullable=False, default=list)
    raw_html = Column(Text, nullable=True)  # Stores raw scraped HTML for reference
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # Relationship to questions
    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    """
    Represents a single quiz question with options and metadata.
    Linked to a parent Quiz via foreign key.
    """

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of 4 option strings
    answer = Column(String(500), nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    explanation = Column(Text, nullable=False)

    # Relationship back to quiz
    quiz = relationship("Quiz", back_populates="questions")
