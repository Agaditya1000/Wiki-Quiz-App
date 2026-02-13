# Wiki Quiz App 📚

Generate AI-powered quizzes from any Wikipedia article. Built with **FastAPI**, **Google Gemini 2.5 Flash**, **PostgreSQL**, and **React**.

**GitHub Repository:** [Wiki-Quiz-App](https://github.com/Agaditya1000/Wiki-Quiz-App)

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
| Backend | **FastAPI** (Python 3.10+) |
| LLM | **Google Gemini 2.5 Flash** via **google-genai SDK** |
| Database | **PostgreSQL** (Neon/Local) |
| Scraping | **BeautifulSoup4** |
| Frontend | **React** (Vite + Tailwind/CSS) |

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **PostgreSQL** (Local or Cloud like Neon)
- **Gemini API Key** — Get a free key from [Google AI Studio](https://aistudio.google.com/apikey)

## Setup & Run

### 1. Backend

```bash
cd backend

# Create virtual environment (optional, one already exists in backend/venv)
python -m venv venv
# Windows:
.\venv\Scripts\activate
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
DATABASE_URL=postgresql://user:password@localhost:5432/wiki_quiz
GEMINI_API_KEY=AIzaSy...
```

**Start the server:**
```bash
# Using npm script (recommended)
npm start

# OR manually
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`.

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

## Project Structure

```
Wiki Quiz App/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & Env vars
│   │   ├── database.py          # SQLAlchemy session
│   │   ├── models.py            # DB Tables (Quiz, Question)
│   │   ├── schemas.py           # Pydantic models
│   │   ├── routers/
│   │   │   └── quiz.py          # API endpoints
│   │   └── services/
│   │       ├── scraper.py       # Wikipedia scraper
│   │       └── llm.py           # Gemini 2.5 Flash integration
│   ├── requirements.txt
│   ├── .env                     # Secrets (ignored by git)
│   ├── .env.example             # Example secrets
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main layout
│   │   ├── components/          # React components
│   │   └── index.css            # Styles
├── sample_data/                 # Test coding samples
└── README.md
```

## Error Handling

- **Invalid URLs**: Validates Wikipedia format.
- **Rate Limits**: Auto-retries Gemini API calls with exponential backoff.
- **Content Truncation**: Automatically truncates very long articles to fit context window.
