"""
API router for quiz-related endpoints.
Handles quiz generation, history listing, and detail retrieval.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Quiz, Question
from app.schemas import (
    QuizRequest,
    QuizResponse,
    QuizListItem,
    QuestionResponse,
    KeyEntities,
    PreviewResponse,
)
from app.services.scraper import scrape_wikipedia, get_article_title
from app.services.llm import generate_quiz

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


# ── POST /api/quiz/generate ─────────────────────────────────────────────────


@router.post("/generate", response_model=QuizResponse)
def generate_quiz_endpoint(request: QuizRequest, db: Session = Depends(get_db)):
    """
    Generate a quiz from a Wikipedia article URL.

    Steps:
    1. Check if the URL has already been processed (caching).
    2. Scrape the Wikipedia article using BeautifulSoup.
    3. Generate quiz questions and extract entities using Gemini LLM.
    4. Store everything in the PostgreSQL database.
    5. Return the full quiz response as JSON.
    """
    url = request.url.strip()

    # ── Step 1: Check cache (prevent duplicate scraping) ─────────────────
    existing = db.query(Quiz).filter(Quiz.url == url).first()
    if existing:
        return _build_quiz_response(existing)

    # ── Step 2: Scrape the Wikipedia article ─────────────────────────────
    try:
        article = scrape_wikipedia(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while scraping: {str(e)}",
        )

    # ── Step 3: Generate quiz via LLM ────────────────────────────────────
    try:
        generated = generate_quiz(
            title=article.title,
            content=article.full_text,
            num_questions=7,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during quiz generation: {str(e)}",
        )

    if not generated.quiz:
        raise HTTPException(
            status_code=500,
            detail="The LLM failed to generate valid quiz questions. Please try again.",
        )

    # ── Step 4: Store in database ────────────────────────────────────────
    quiz_record = Quiz(
        url=url,
        title=article.title,
        summary=article.summary,
        key_entities=generated.key_entities,
        sections=article.sections,
        related_topics=generated.related_topics,
        raw_html=article.raw_html,
    )
    db.add(quiz_record)
    db.flush()  # Get the quiz ID before adding questions

    for q in generated.quiz:
        question_record = Question(
            quiz_id=quiz_record.id,
            question=q["question"],
            options=q["options"],
            answer=q["answer"],
            difficulty=q["difficulty"],
            explanation=q["explanation"],
        )
        db.add(question_record)

    db.commit()
    db.refresh(quiz_record)

    return _build_quiz_response(quiz_record)


# ── GET /api/quiz/history ────────────────────────────────────────────────────


@router.get("/history", response_model=list[QuizListItem])
def get_quiz_history(db: Session = Depends(get_db)):
    """
    Retrieve a list of all previously generated quizzes.
    Returns abbreviated info (no full questions) for the history table.
    """
    quizzes = db.query(Quiz).order_by(Quiz.created_at.desc()).all()

    return [
        QuizListItem(
            id=quiz.id,
            url=quiz.url,
            title=quiz.title,
            summary=quiz.summary[:200] + "..." if len(quiz.summary) > 200 else quiz.summary,
            question_count=len(quiz.questions),
            created_at=quiz.created_at,
        )
        for quiz in quizzes
    ]


# ── GET /api/quiz/{quiz_id} ─────────────────────────────────────────────────


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz_detail(quiz_id: int, db: Session = Depends(get_db)):
    """
    Retrieve full details of a specific quiz by its ID.
    Used by the "Details" modal in the history tab.
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")

    return _build_quiz_response(quiz)


# ── GET /api/quiz/preview ────────────────────────────────────────────────────


@router.get("/preview/url", response_model=PreviewResponse)
def preview_url(url: str = Query(..., description="Wikipedia article URL")):
    """
    Quick URL validation and title preview.
    Fetches just the article title without full scraping.
    """
    try:
        title = get_article_title(url)
        return PreviewResponse(title=title, url=url, valid=True)
    except (ValueError, ConnectionError) as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Helper ───────────────────────────────────────────────────────────────────


def _build_quiz_response(quiz: Quiz) -> QuizResponse:
    """Convert a Quiz ORM model instance to a QuizResponse schema."""
    entities = quiz.key_entities or {"people": [], "organizations": [], "locations": []}

    return QuizResponse(
        id=quiz.id,
        url=quiz.url,
        title=quiz.title,
        summary=quiz.summary,
        key_entities=KeyEntities(**entities),
        sections=quiz.sections or [],
        quiz=[
            QuestionResponse(
                question=q.question,
                options=q.options,
                answer=q.answer,
                difficulty=q.difficulty,
                explanation=q.explanation,
            )
            for q in quiz.questions
        ],
        related_topics=quiz.related_topics or [],
        created_at=quiz.created_at,
    )
