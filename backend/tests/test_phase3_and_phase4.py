"""Unit tests for Phase 3 (AQI/Weather/Locations) and Phase 4 (RAG knowledge base)."""
import uuid
from datetime import datetime, timezone

from app.main import app
from app.modules.air_quality_readings.service import AirQualityService
from app.modules.document_chunks.repository import cosine_similarity
from app.modules.document_chunks.schema import DocumentChunkWithScore
from app.modules.knowledge_documents.service import KnowledgeDocumentService
from app.modules.locations.schema import LocationResponse, LocationWithEnvironmentalData
from app.modules.rag.service import RAGService
from app.modules.weather_readings.service import WeatherService


def test_phase4_dependencies_importable():
    import bs4  # noqa: F401
    import pypdf  # noqa: F401
    import sentence_transformers  # noqa: F401

    assert app is not None


def test_openaq_v3_aqi_and_unit_normalization():
    svc = AirQualityService(None)
    assert svc._pm25_to_aqi(12.05) == 50
    assert svc._pm25_to_aqi(35.4) == 100
    assert svc._pm10_to_aqi(54) == 50
    assert svc._normalize_value("co", 500.0, "µg/m³") == 0.5
    assert svc._normalize_value("pm25", -999.0, "µg/m³") is None


def test_weather_parsing_and_location_schema():
    wsvc = WeatherService(None)
    reading = wsvc._parse_openweather_response(
        {
            "main": {"temp": 28.5, "humidity": 60, "pressure": 1012},
            "wind": {"speed": 3.2, "deg": 180},
            "weather": [{"id": 800}],
            "clouds": {"all": 10},
            "rain": {"1h": 0.5},
            "visibility": 10000,
            "dt": 1700000000,
        }
    )
    assert reading.temperature_c == 28.5
    assert reading.precipitation_mm == 0.5
    assert reading.visibility_km == 10.0

    now = datetime.now(timezone.utc)
    loc = LocationResponse(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        name="Bengaluru",
        lat=12.9716,
        lon=77.5946,
        is_default=True,
        created_at=now,
        updated_at=now,
    )
    combined = LocationWithEnvironmentalData(
        **loc.model_dump(), latest_aqi=None, latest_weather=None
    )
    assert combined.lat == 12.9716


def test_chunk_pages_preserves_page_numbers():
    svc = KnowledgeDocumentService(None)
    pages = [
        (1, "WHO PM2.5 guideline is 5 micrograms per cubic meter annual mean."),
        (2, "CPCB National AQI classifies 0 to 50 as Good air quality."),
    ]
    chunked = svc._chunk_pages(pages)
    assert len(chunked) == 2
    assert chunked[0][0] == 1
    assert chunked[1][0] == 2


def test_cosine_similarity_and_rag_prompt_formatting():
    assert round(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 5) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0

    rag = RAGService(None)
    chunk = DocumentChunkWithScore(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        chunk_index=0,
        page_number=3,
        content="Avoid outdoor vigorous exercise when PM2.5 is very high.",
        token_count=10,
        similarity_score=0.88,
        document_title="WHO Air Quality Guidelines",
        document_source_url="https://www.who.int/",
        document_source_type="pdf",
    )
    formatted = rag.format_retrieved_documents([chunk])
    assert "[pdf] WHO Air Quality Guidelines (p. 3)" in formatted
    assert "0.88" in formatted
