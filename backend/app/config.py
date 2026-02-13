"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from .env file or environment variables.
    """

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/wiki_quiz"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
