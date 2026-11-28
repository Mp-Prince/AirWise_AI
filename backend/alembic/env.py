from logging.config import fileConfig
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.database.base import Base
from app.core.config import get_settings

# Import all models so they're registered with Base.metadata
from app.modules.users.models import UserModel
from app.modules.user_profiles.models import UserProfileModel
from app.modules.locations.models import LocationModel
from app.modules.families.models import FamilyModel
from app.modules.family_members.models import FamilyMemberModel
from app.modules.air_quality_readings.models import AirQualityReadingModel
from app.modules.weather_readings.models import WeatherReadingModel
from app.modules.daily_routines.models import DailyRoutineModel
from app.modules.recommendations.models import RecommendationModel
from app.modules.user_actions.models import UserActionModel
from app.modules.emission_factors.models import EmissionFactorModel
from app.modules.impact_records.models import ImpactRecordModel
from app.modules.knowledge_documents.models import KnowledgeDocumentModel
from app.modules.document_chunks.models import DocumentChunkModel
from app.modules.chat_conversations.models import ChatConversationModel
from app.modules.chat_messages.models import ChatMessageModel
from app.modules.rag.models import KnowledgeAuditLogModel

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from our settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()