cd D:/Prompt_War/AirWise_AI
git commit -m "Phase 1: Database models and migrations

- Created 16 entity modules with SQLAlchemy 2.0 Mapped models
- Fixed type mappings: dict->JSON, list->ARRAY, relationship column rename
- Document chunks embedding changed from pgvector Vector to JSON (pgvector not available)
- Added alembic configuration with all model imports
- Generated initial migration for all 16 core tables + indexes + FKs
- Applied migration successfully - all 17 tables created in PostgreSQL
- Backend health endpoint verified at /api/v1/health

Co-Authored-By: Claude Code <noreply@anthropic.com>"