"""
LLM-powered quiz generation using Google Gemini 1.5 Flash.
Uses the google-genai SDK directly for best compatibility and control.
"""

import json
import re
import time
from dataclasses import dataclass, field

from google import genai
from google.genai import types

from app.config import settings


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

QUIZ_PROMPT = """You are an expert quiz creator. Generate {num_questions} high-quality 
multiple-choice questions from this Wikipedia article.

RULES:
- Each question MUST be answerable from the article text below.
- Distribute difficulty: ~30% easy, ~40% medium, ~30% hard.
- Each question has exactly 4 options with one correct answer.
- Return ONLY valid JSON, no markdown fences, no extra text.

FORMAT:
{{"quiz": [{{"question": "...", "options": ["A","B","C","D"], "answer": "correct option text", "difficulty": "easy|medium|hard", "explanation": "..."}}]}}

TITLE: {title}

ARTICLE:
{content}

Return ONLY the JSON object."""


ENTITY_PROMPT = """Extract key entities and suggest related topics from this article.

RULES:
- Only extract entities actually mentioned in the text.
- Suggest 3-5 related Wikipedia topics.
- Return ONLY valid JSON, no markdown fences, no extra text.

FORMAT:
{{"key_entities": {{"people": [], "organizations": [], "locations": []}}, "related_topics": []}}

TITLE: {title}

ARTICLE:
{content}

Return ONLY the JSON object."""


# ══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ══════════════════════════════════════════════════════════════════════════════


@dataclass
class GeneratedQuiz:
    """Complete output from the LLM quiz generation pipeline."""

    quiz: list[dict] = field(default_factory=list)
    key_entities: dict = field(default_factory=lambda: {
        "people": [], "organizations": [], "locations": []
    })
    related_topics: list[str] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════════════════
# LLM SERVICE
# ══════════════════════════════════════════════════════════════════════════════

MODEL = "gemini-2.5-flash"
MAX_RETRIES = 3
RETRY_DELAYS = [15, 30, 60]


def _parse_json(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown fences."""
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return json.loads(text)


def _get_client() -> genai.Client:
    """Create a Gemini client."""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to backend/.env. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def _call_gemini(client: genai.Client, prompt: str, label: str = "LLM") -> str:
    """Call Gemini with retry logic for rate limits."""
    for attempt in range(MAX_RETRIES):
        try:
            print(f"[{label}] Calling Gemini 1.5 Flash (attempt {attempt + 1})...")
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=4096,
                ),
            )
            text = response.text
            if text:
                print(f"[{label}] Success! ({len(text)} chars)")
                return text
            else:
                print(f"[{label}] Empty response, retrying...")

        except Exception as e:
            err = str(e).lower()
            is_rate_limit = any(kw in err for kw in [
                "429", "quota", "rate", "resource_exhausted", "too many"
            ])
            if is_rate_limit and attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAYS[attempt]
                print(f"[{label}] Rate limited. Waiting {delay}s...")
                time.sleep(delay)
            else:
                raise

    raise RuntimeError(f"[{label}] All retries exhausted.")


def generate_quiz(title: str, content: str, num_questions: int = 7) -> GeneratedQuiz:
    """Generate quiz from article content using Gemini 1.5 Flash."""
    client = _get_client()
    result = GeneratedQuiz()

    num_questions = max(5, min(10, num_questions))

    # Truncate long articles
    MAX_LEN = 10000
    if len(content) > MAX_LEN:
        content = content[:MAX_LEN] + "\n\n[Truncated]"
        print(f"[LLM] Article truncated to {MAX_LEN} chars")

    # ── Step 1: Generate quiz ────────────────────────────────────────────
    try:
        prompt = QUIZ_PROMPT.format(
            num_questions=num_questions, title=title, content=content
        )
        raw = _call_gemini(client, prompt, label="Quiz")
        data = _parse_json(raw)
        questions = data.get("quiz", [])

        # Validate
        validated = []
        for q in questions:
            if all(k in q for k in ("question", "options", "answer", "difficulty", "explanation")):
                if q["difficulty"] not in ("easy", "medium", "hard"):
                    q["difficulty"] = "medium"
                if len(q["options"]) == 4:
                    validated.append(q)
        result.quiz = validated

    except Exception as e:
        print(f"[Quiz] Error: {e}")

    # Delay between calls
    time.sleep(3)

    # ── Step 2: Extract entities ─────────────────────────────────────────
    try:
        prompt = ENTITY_PROMPT.format(title=title, content=content)
        raw = _call_gemini(client, prompt, label="Entities")
        data = _parse_json(raw)
        result.key_entities = data.get("key_entities", {
            "people": [], "organizations": [], "locations": []
        })
        result.related_topics = data.get("related_topics", [])

    except Exception as e:
        print(f"[Entities] Error: {e}")

    return result
