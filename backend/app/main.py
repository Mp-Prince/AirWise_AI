"""AirWise AI FastAPI application entry point.

Phase 0: app boot + health check only. Entity module routers
(app/modules/<entity>/module.py) are mounted as each phase lands them.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.modules.users.module import router as auth_router

# Import all model modules to register them with SQLAlchemy
import app.modules.users.repository
import app.modules.user_profiles.repository

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Air quality, planning and impact platform API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount auth router
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"app": settings.APP_NAME, "status": "ok"}


@app.get(f"{settings.API_V1_PREFIX}/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "healthy", "env": settings.APP_ENV}
