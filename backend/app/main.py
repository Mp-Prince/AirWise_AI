"""AirWise AI FastAPI application entry point.

Phase 0: app boot + health check only. Entity module routers
(app/modules/<entity>/routes.py) are mounted as each phase lands them.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.modules.users.routes import router as auth_router
from app.modules.user_profiles.routes import router as profile_router
from app.modules.locations.routes import router as locations_router
from app.modules.air_quality_readings.routes import router as air_quality_router
from app.modules.weather_readings.routes import router as weather_router
from app.modules.knowledge_documents.module import router as knowledge_documents_router
from app.modules.document_chunks.module import router as document_chunks_router
from app.modules.rag.module import router as rag_router
from app.modules.assistant.module import router as assistant_router
from app.modules.daily_routines.module import router as routines_router
from app.modules.recommendations.module import router as recommendations_router
from app.modules.emission_factors.module import router as emission_factors_router
from app.modules.impact_records.module import router as impact_router

# Import all model modules to register them with SQLAlchemy
import app.modules.users.models
import app.modules.user_profiles.models
import app.modules.locations.models
import app.modules.air_quality_readings.models
import app.modules.weather_readings.models
import app.modules.knowledge_documents.models
import app.modules.document_chunks.models
import app.modules.rag.models
import app.modules.chat_conversations.models
import app.modules.chat_messages.models
import app.modules.user_actions.models
import app.modules.daily_routines.models
import app.modules.recommendations.models
import app.modules.emission_factors.models
import app.modules.impact_records.models

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
app.include_router(auth_router, prefix=settings.API_V1_PREFIX + "/auth")
# Mount profile router (Phase 2)
app.include_router(profile_router, prefix=settings.API_V1_PREFIX + "/profile")
# Mount Phase 3 routers
app.include_router(locations_router, prefix=settings.API_V1_PREFIX + "/locations")
app.include_router(air_quality_router, prefix=settings.API_V1_PREFIX + "/air-quality")
app.include_router(weather_router, prefix=settings.API_V1_PREFIX + "/weather")
# Mount Phase 4 routers
app.include_router(knowledge_documents_router, prefix=settings.API_V1_PREFIX + "/knowledge")
app.include_router(document_chunks_router, prefix=settings.API_V1_PREFIX + "/chunks")
app.include_router(rag_router, prefix=settings.API_V1_PREFIX + "/rag")
# Mount Phase 5 router
app.include_router(assistant_router, prefix=settings.API_V1_PREFIX + "/assistant")
# Mount Phase 6 routers
app.include_router(routines_router, prefix=settings.API_V1_PREFIX + "/routines")
app.include_router(recommendations_router, prefix=settings.API_V1_PREFIX + "/recommendations")
# Mount Phase 7 routers
app.include_router(emission_factors_router, prefix=settings.API_V1_PREFIX + "/emission-factors")
app.include_router(impact_router, prefix=settings.API_V1_PREFIX + "/impact")


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"app": settings.APP_NAME, "status": "ok"}


@app.get(f"{settings.API_V1_PREFIX}/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "healthy", "env": settings.APP_ENV}
