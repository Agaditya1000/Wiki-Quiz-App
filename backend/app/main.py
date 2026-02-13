"""
FastAPI application entry point.
Configures CORS, includes routers, and creates database tables on startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import quiz


# ── Lifespan: create tables on startup ───────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all database tables on application startup."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully.")
    yield


# ── App Instance ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Wiki Quiz API",
    description=(
        "Generates quizzes from Wikipedia articles using LLM. "
        "Scrapes article content, creates MCQ questions, and stores results."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── CORS Middleware (allow frontend dev server) ──────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Register Routers ────────────────────────────────────────────────────────

app.include_router(quiz.router)


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "Wiki Quiz API",
        "version": "1.0.0",
    }
