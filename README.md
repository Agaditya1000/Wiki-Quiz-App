# Wiki Quiz App 📚

Generate AI-powered quizzes from any Wikipedia article. Built with **FastAPI**, **LangChain + Gemini**, **PostgreSQL**, and **React**.

![Tab 1 - Generate Quiz](screenshots/tab1_generate.png)

## Features

- 🎯 **Quiz Generation** — Paste a Wikipedia URL and get 5-10 MCQ questions with difficulty levels, explanations, and related topics
- 📋 **Quiz History** — Browse all previously generated quizzes in a table with "Details" modal
- 🎮 **Take Quiz Mode** — Interactive quiz with hidden answers, scoring, and feedback
- 🔗 **URL Preview** — Auto-fetches article title for validation before generating
- ⚡ **Caching** — Same URL returns cached results (no duplicate scraping)
- 🧠 **Entity Extraction** — Identifies people, organizations, and locations from articles
- 📑 **Section Detection** — Lists all article sections covered
- 💾 **Raw HTML Storage** — Stores original scraped HTML for reference

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | **FastAPI** (Python) |
| LLM | **Google Gemini 2.0 Flash** via **LangChain** |
| Database | **PostgreSQL** |
| Scraping | **BeautifulSoup4** |
| Frontend | **React** (Vite) |

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** (one of the options below)
- **Gemini API Key** — Free from [Google AI Studio](https://aistudio.google.com/apikey)

### PostgreSQL Setup

**Option 1 — Local Install (Recommended):**
Install from [postgresql.org](https://www.postgresql.org/download/), then:
```sql
CREATE DATABASE wiki_quiz;
```

**Option 2 — Cloud (Neon/Supabase):**
Create a free database and use the connection URL in your `.env`.

## Setup & Run

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and DATABASE_URL
```

**`.env` file:**
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/wiki_quiz
GEMINI_API_KEY=your_api_key_here
```

**Start the server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/quiz/generate` | Generate quiz from Wikipedia URL |
| `GET` | `/api/quiz/history` | List all past quizzes |
| `GET` | `/api/quiz/{id}` | Get full quiz details by ID |
| `GET` | `/api/quiz/preview/url?url=...` | Preview URL (fetch title) |
| `GET` | `/` | Health check |

### Example — Generate Quiz

```bash
curl -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Alan_Turing"}'
```

### Sample API Response

```json
{
  "id": 1,
  "url": "https://en.wikipedia.org/wiki/Alan_Turing",
  "title": "Alan Turing",
  "summary": "Alan Turing was a British mathematician...",
  "key_entities": {
    "people": ["Alan Turing", "Alonzo Church"],
    "organizations": ["University of Cambridge", "Bletchley Park"],
    "locations": ["United Kingdom"]
  },
  "sections": ["Early life", "World War II", "Legacy"],
  "quiz": [
    {
      "question": "Where did Alan Turing study?",
      "options": ["Harvard University", "Cambridge University", "Oxford University", "Princeton University"],
      "answer": "Cambridge University",
      "difficulty": "easy",
      "explanation": "Mentioned in the 'Early life' section."
    }
  ],
  "related_topics": ["Cryptography", "Enigma machine", "Computer science history"]
}
```

## LangChain Prompt Templates

### Quiz Generation Prompt

The quiz generation prompt instructs the LLM to:
- Generate exactly N questions from the provided article text only
- Include question text, 4 options (A-D), correct answer, difficulty (easy/medium/hard), and explanation
- Distribute difficulty: ~30% easy, ~40% medium, ~30% hard
- Ground all questions in the article content (no hallucination)
- Return structured JSON output

See [`backend/app/services/llm.py`](backend/app/services/llm.py) for the full `QUIZ_GENERATION_PROMPT` template.

### Entity & Topic Extraction Prompt

The entity extraction prompt instructs the LLM to:
- Extract people, organizations, and locations mentioned in the article
- Suggest 3-5 related Wikipedia topics for further reading
- Return structured JSON output

See [`backend/app/services/llm.py`](backend/app/services/llm.py) for the full `ENTITY_TOPIC_PROMPT` template.

## Project Structure

```
Wiki Quiz App/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings (env variables)
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models.py            # ORM models (Quiz, Question)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   └── quiz.py          # API endpoints
│   │   └── services/
│   │       ├── scraper.py       # BeautifulSoup Wikipedia scraper
│   │       └── llm.py           # LangChain + Gemini quiz generation
│   ├── requirements.txt
│   ├── .env / .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Root component with tabs
│   │   ├── main.jsx             # Entry point
│   │   ├── index.css            # Full design system
│   │   └── components/
│   │       ├── GenerateQuiz.jsx  # Tab 1 - URL input & quiz display
│   │       ├── PastQuizzes.jsx   # Tab 2 - History table
│   │       ├── QuizDisplay.jsx   # Card-based quiz layout
│   │       ├── QuizModal.jsx     # Details modal
│   │       └── TakeQuiz.jsx      # Interactive quiz mode
├── sample_data/
│   ├── urls.txt                  # Test URLs
│   └── alan_turing_output.json   # Sample API output
└── README.md
```

## Testing

1. Start PostgreSQL
2. Start backend (`uvicorn app.main:app --reload`)
3. Start frontend (`npm run dev`)
4. Open `http://localhost:5173`
5. Enter a Wikipedia URL (e.g., `https://en.wikipedia.org/wiki/Alan_Turing`)
6. Click "Generate Quiz" and wait ~15-30 seconds
7. Verify quiz displays with questions, entities, sections, and related topics
8. Switch to "Past Quizzes" tab to verify history
9. Click "Details" on a quiz to verify the modal
10. Click "Take Quiz" to test the interactive quiz mode

## Error Handling

- **Invalid URLs** — Validates Wikipedia URL format before processing
- **Network errors** — Graceful error messages for failed scraping
- **LLM failures** — Falls back with clear error if quiz generation fails
- **Missing API key** — Informative error directing to Google AI Studio
