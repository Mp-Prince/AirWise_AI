# AirWise AI

*Smarter choices for cleaner air.*

AI-powered air-quality companion for India: sourced AQI/weather data, a RAG-grounded
assistant, personalized sustainable recommendations, a daily planner, an impact
tracker and optional family groups.

## Project layout

```text
AirWise_AI/
├── .md/                 # Project requirements documentation (source of truth)
├── frontend/
│   └── web/             # React + Bootstrap 5.3 responsive web app (Vite)
└── backend/             # Python + FastAPI REST API
    ├── .venv/           # Python virtual environment (venv — NOT uv), never committed
    └── app/
        ├── main.py      # FastAPI entry point, registers module routers
        ├── core/        # config, security, dependencies
        ├── database/    # SQLAlchemy connection + base
        ├── modules/     # one folder per DB table/entity
        │   └── <entity>/module.py · schema.py · repository.py · service.py
        ├── integrations/# external API clients (AQI, weather, LLM, embeddings…)
        └── utils/
```

## Tech stack

| Layer     | Technology                                             |
|-----------|--------------------------------------------------------|
| Frontend  | React.js, Bootstrap 5.3, React Router, Axios, TanStack Query, Chart.js |
| Backend   | Python, FastAPI, Pydantic, SQLAlchemy, `venv`          |
| Database  | PostgreSQL + pgvector                                  |
| AI        | LLM + RAG over trusted environmental documents         |

> Note: backend environment management uses Python's built-in `venv` with `pip` and
> `requirements.txt`. This is the current instruction and supersedes the `uv`
> references in `.md/07_Backend_Structure.md`.

## Development setup

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
fastapi dev app/main.py     # API docs at http://127.0.0.1:8000/docs
```

Copy `backend/.env.example` to `backend/.env` and fill in real values. Never commit `.env`.

### Frontend

```powershell
cd frontend\web
npm install
npm run dev                 # app at http://127.0.0.1:5173
```

Copy `frontend/web/.env.example` to `frontend/web/.env.local` if needed.
No API keys may ever live in frontend environment variables.

### Database

PostgreSQL 15+ with the pgvector extension enabled:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Development process

Built incrementally per `.md/05_Development_Phases.md` (Phase 0 → Phase 10).
Each phase ends with a mandatory Git commit + push checkpoint; the next phase
starts only after the push is confirmed.
