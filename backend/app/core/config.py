"""Application settings loaded from backend/.env (never committed)."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Explicitly point to backend/.env regardless of working directory
BACKEND_ENV = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ENV), env_file_encoding="utf-8", extra="ignore"
    )

    # All values loaded from backend/.env — no hardcoded defaults
    APP_NAME: str
    APP_ENV: str
    API_V1_PREFIX: str
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    CORS_ORIGINS: str

    # External providers — keys stay server-side only (Phase 3+)
    OPENAQ_API_KEY: str = ""
    GEOCODING_API_KEY: str = ""
    LLM_API_KEY: str = ""
    EMBEDDING_API_KEY: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
