"""
Pydantic schemas for API request/response validation.
Defines the data contracts between frontend and backend.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


# ── Request Schemas ──────────────────────────────────────────────────────────


class QuizRequest(BaseModel):
    """Request body for quiz generation endpoint."""

    url: str

    @field_validator("url")
    @classmethod
    def validate_wikipedia_url(cls, v: str) -> str:
        """Ensure the URL is a valid Wikipedia article URL."""
        v = v.strip()
        if not v.startswith("http"):
            raise ValueError("URL must start with http:// or https://")
        if "wikipedia.org/wiki/" not in v:
            raise ValueError("URL must be a valid Wikipedia article URL")
        return v


# ── Response Schemas ─────────────────────────────────────────────────────────


class QuestionResponse(BaseModel):
    """Schema for a single quiz question in the API response."""

    question: str
    options: list[str]
    answer: str
    difficulty: str
    explanation: str

    class Config:
        from_attributes = True


class KeyEntities(BaseModel):
    """Schema for extracted key entities from the article."""

    people: list[str] = []
    organizations: list[str] = []
    locations: list[str] = []


class QuizResponse(BaseModel):
    """Full quiz response matching the required API output format."""

    id: int
    url: str
    title: str
    summary: str
    key_entities: KeyEntities
    sections: list[str]
    quiz: list[QuestionResponse]
    related_topics: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class QuizListItem(BaseModel):
    """Abbreviated quiz info for the history list endpoint."""

    id: int
    url: str
    title: str
    summary: str
    question_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PreviewResponse(BaseModel):
    """Response for URL preview / validation endpoint."""

    title: str
    url: str
    valid: bool


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str
