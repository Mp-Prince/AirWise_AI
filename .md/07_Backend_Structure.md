# AirWise AI – Backend Folder Structure

## 1. Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| Backend framework | FastAPI |
| Environment and package management | uv |
| Database | PostgreSQL |
| Vector database extension | pgvector |
| ORM / database toolkit | SQLAlchemy |
| Request and response validation | Pydantic |
| API documentation | FastAPI Swagger UI |

## 2. Architecture Rules

Each database table/entity has its own module folder. Each module contains:

- `module.py` – declares the FastAPI router and API endpoints.
- `schema.py` – defines Pydantic request and response schemas.
- `repository.py` – contains database access and CRUD queries.
- `service.py` – contains business rules and application logic.

**Router placement:** Define the router in that module's `module.py`. Do not create a separate router file for each module.

Shared application configuration, database connection, security, and utilities belong in shared folders outside `modules/`.

## 3. Backend Folder Structure

```text
backend/
│
├── pyproject.toml
├── uv.lock
├── .env
├── .env.example
├── .gitignore
│
└── app/
    │
    ├── main.py
    │
    ├── core/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── security.py
    │   └── dependencies.py
    │
    ├── database/
    │   ├── __init__.py
    │   ├── connection.py
    │   └── base.py
    │
    ├── modules/
    │   │
    │   ├── users/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── user_profiles/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── locations/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── families/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── family_members/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── air_quality_readings/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── weather_readings/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── daily_routines/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── recommendations/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── user_actions/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── emission_factors/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── impact_records/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── knowledge_documents/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── document_chunks/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   ├── chat_conversations/
    │   │   ├── __init__.py
    │   │   ├── module.py
    │   │   ├── schema.py
    │   │   ├── repository.py
    │   │   └── service.py
    │   │
    │   └── chat_messages/
    │       ├── __init__.py
    │       ├── module.py
    │       ├── schema.py
    │       ├── repository.py
    │       └── service.py
    │
    ├── integrations/
    │   ├── __init__.py
    │   ├── air_quality_provider.py
    │   ├── weather_provider.py
    │   └── llm_provider.py
    │
    └── utils/
        ├── __init__.py
        └── helpers.py
```

The structure above includes the core tables from the proposed database design. Optional tables such as `family_goals`, `notifications`, `api_sync_logs`, `document_ingestion_jobs`, and `user_consents` can be added using the same four-file module pattern if they are included in the final schema.

## 4. Responsibility of Each File

| File | Responsibility | Example |
|---|---|---|
| `module.py` | API routes and HTTP handling | `POST /users/` |
| `schema.py` | Input/output validation | `UserCreate`, `UserResponse` |
| `repository.py` | Database queries | Insert, fetch, update, delete |
| `service.py` | Business logic | Validate rules, hash passwords, coordinate repository calls |

### Request flow

```text
React frontend
      |
      v
module.py
(FastAPI endpoint/router)
      |
      v
schema.py
(Validate request data)
      |
      v
service.py
(Business logic)
      |
      v
repository.py
(Database operations)
      |
      v
PostgreSQL
```

A response returns through the service and module layers to the frontend. The repository should focus on data access; business rules should stay in the service layer.

## 5. Example Users Module

### `modules/users/module.py`

```python
from fastapi import APIRouter, Depends
from .schema import UserCreate, UserResponse
from .service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate):
    return UserService.create_user(payload)
```

### `modules/users/schema.py`

```python
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
```

### `modules/users/repository.py`

```python
class UserRepository:

    @staticmethod
    def create(db, user_data: dict):
        # Add and commit the user using the database session.
        # Return the saved user.
        pass
```

### `modules/users/service.py`

```python
from .repository import UserRepository


class UserService:

    @staticmethod
    def create_user(payload):
        # Apply business rules and securely hash the password.
        # Call UserRepository.create(...) with the database session.
        pass
```

This is an architectural example, not complete runnable CRUD code. The database session dependency, password hashing, duplicate-email handling, and error handling must be implemented before using it.

## 6. Registering Module Routers

Each module exports its router from `module.py`. The application entry point imports and registers those routers.

### `app/main.py`

```python
from fastapi import FastAPI

from app.modules.users.module import router as users_router
from app.modules.user_profiles.module import router as profiles_router
from app.modules.locations.module import router as locations_router

app = FastAPI(
    title="AirWise AI API",
    version="1.0.0"
)

app.include_router(users_router, prefix="/api/v1")
app.include_router(profiles_router, prefix="/api/v1")
app.include_router(locations_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "AirWise AI API is running"}
```

As new modules are implemented, import and register their routers in `main.py`.

## 7. Initialize the Backend with uv

Run these commands from the project directory:

```bash
mkdir backend
cd backend

uv init
uv add "fastapi[standard]" sqlalchemy "psycopg[binary]" pydantic-settings email-validator
```

Start the development server:

```bash
uv run fastapi dev app/main.py
```

Open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## 8. Environment Variables

Keep credentials and secrets in `.env`. Do not commit `.env` to Git. Commit `.env.example` with placeholder values instead.

Example `.env.example`:

```env
APP_NAME=AirWise AI
APP_ENV=development
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/airwise_ai
SECRET_KEY=replace_with_a_secure_secret
```

Load settings through `core/config.py`; do not hard-code credentials in modules.

## 9. Important Development Guidelines

1. Keep one module per database table/entity.
2. Keep the four-file pattern consistent across modules.
3. Define each module's router in its `module.py`.
4. Keep SQL/database queries in `repository.py`.
5. Keep business logic in `service.py`.
6. Use Pydantic models in `schema.py` for request and response validation.
7. Share database sessions through FastAPI dependencies.
8. Use SQLAlchemy models/migrations consistently with the database schema.
9. Keep external API clients in `integrations/`, not inside table repositories.
10. Add authentication and authorization checks before exposing user or family data.
11. Use transactions for operations that update related records.
12. Never return password hashes, API keys, or private configuration in API responses.

---

**Agreed backend convention:** Python + FastAPI + uv, PostgreSQL + pgvector, table-wise modules, and each module's router defined in its own `module.py`. This document defines the folder structure; implementation details can be added as each module is developed.
