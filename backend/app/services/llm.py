"""
LLM-powered quiz generation service using LangChain and Google Gemini.
Contains prompt templates for quiz generation and entity/topic extraction.
"""

import json
import re
from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from app.config import settings


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

# ── Quiz Generation Prompt ───────────────────────────────────────────────────
QUIZ_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert quiz creator. Your task is to generate high-quality 
multiple-choice quiz questions from Wikipedia article content.

RULES:
- Generate exactly {num_questions} questions.
- Each question MUST be directly answerable from the provided article text.
- Do NOT invent facts or use knowledge outside the article.
- Questions should cover different sections and topics from the article.
- Distribute difficulty levels: roughly 30% easy, 40% medium, 30% hard.
- Each question must have exactly 4 options (A-D) with only one correct answer.
- Explanations should reference which part of the article contains the answer.
- Options should be plausible and not obviously wrong.

OUTPUT FORMAT — respond with ONLY valid JSON (no markdown, no extra text):
{{
  "quiz": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct option text (must exactly match one of the options)",
      "difficulty": "easy|medium|hard",
      "explanation": "Brief explanation referencing the article content."
    }}
  ]
}}""",
        ),
        (
            "human",
            """Generate a quiz from this Wikipedia article:

TITLE: {title}

ARTICLE CONTENT:
{content}

Generate exactly {num_questions} questions. Return ONLY valid JSON.""",
        ),
    ]
)


# ── Entity & Topic Extraction Prompt ─────────────────────────────────────────
ENTITY_TOPIC_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at extracting structured information from text.
Extract key entities and suggest related Wikipedia topics from the article.

RULES:
- Extract real entities mentioned in the article text only.
- Categorize entities into: people, organizations, locations.
- Suggest 3-5 related Wikipedia topics that a reader might find interesting.
- Related topics should be real Wikipedia article subjects.

OUTPUT FORMAT — respond with ONLY valid JSON (no markdown, no extra text):
{{
  "key_entities": {{
    "people": ["Person 1", "Person 2"],
    "organizations": ["Org 1", "Org 2"],
    "locations": ["Location 1", "Location 2"]
  }},
  "related_topics": ["Topic 1", "Topic 2", "Topic 3"]
}}""",
        ),
        (
            "human",
            """Extract entities and suggest related topics from this Wikipedia article:

TITLE: {title}

ARTICLE CONTENT:
{content}

Return ONLY valid JSON.""",
        ),
    ]
)


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


def _parse_json_response(text: str) -> dict:
    """
    Robustly parse JSON from LLM response text.
    Handles markdown code fences and extra text around JSON.
    """
    # Remove markdown code fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Try to find JSON object in the text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    # If all else fails, try parsing the whole text
    return json.loads(text)


def _get_llm() -> ChatGoogleGenerativeAI:
    """Create and return a configured Gemini LLM instance."""
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add it to your .env file. "
            "Get a free key at https://aistudio.google.com/apikey"
        )
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7,
        max_output_tokens=4096,
    )


def generate_quiz(title: str, content: str, num_questions: int = 7) -> GeneratedQuiz:
    """
    Generate a complete quiz from article content using Gemini LLM.

    Runs two LLM calls:
    1. Quiz generation (questions, options, answers, explanations)
    2. Entity extraction and related topic suggestions

    Args:
        title: The article title.
        content: The article text content.
        num_questions: Number of questions to generate (5-10).

    Returns:
        GeneratedQuiz with questions, entities, and related topics.
    """
    llm = _get_llm()
    result = GeneratedQuiz()

    # Clamp question count to valid range
    num_questions = max(5, min(10, num_questions))

    # ── Step 1: Generate quiz questions ──────────────────────────────────
    try:
        quiz_chain = QUIZ_GENERATION_PROMPT | llm
        quiz_response = quiz_chain.invoke({
            "title": title,
            "content": content,
            "num_questions": str(num_questions),
        })
        quiz_data = _parse_json_response(quiz_response.content)
        result.quiz = quiz_data.get("quiz", [])

        # Validate and clean up the quiz data
        validated_questions = []
        for q in result.quiz:
            if all(k in q for k in ("question", "options", "answer", "difficulty", "explanation")):
                # Ensure difficulty is valid
                if q["difficulty"] not in ("easy", "medium", "hard"):
                    q["difficulty"] = "medium"
                # Ensure exactly 4 options
                if len(q["options"]) == 4:
                    validated_questions.append(q)
        result.quiz = validated_questions

    except Exception as e:
        print(f"[LLM] Quiz generation error: {e}")
        # Return empty quiz on failure — will be handled by the router
        result.quiz = []

    # ── Step 2: Extract entities and related topics ──────────────────────
    try:
        entity_chain = ENTITY_TOPIC_PROMPT | llm
        entity_response = entity_chain.invoke({
            "title": title,
            "content": content,
        })
        entity_data = _parse_json_response(entity_response.content)
        result.key_entities = entity_data.get("key_entities", {
            "people": [], "organizations": [], "locations": []
        })
        result.related_topics = entity_data.get("related_topics", [])

    except Exception as e:
        print(f"[LLM] Entity extraction error: {e}")
        # Defaults already set in GeneratedQuiz dataclass

    return result
