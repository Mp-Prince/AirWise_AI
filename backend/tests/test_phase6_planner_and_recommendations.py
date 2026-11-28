"""Unit tests for Phase 6 (Daily Planner safety bands & Recommendation rules)."""
from datetime import time

import pytest
from pydantic import ValidationError

from app.modules.daily_routines.schema import DailyRoutineCreate
from app.modules.daily_routines.service import compute_safety_band
from app.modules.recommendations.service import build_deterministic_rules


def test_compute_safety_band_rules():
    assert compute_safety_band("exercise", None, False)[0] == "unknown"
    assert compute_safety_band("indoor_air", None, False)[0] == "safe"
    assert compute_safety_band("exercise", 40, False)[0] == "safe"
    assert compute_safety_band("exercise", 80, False)[0] == "safe"
    assert compute_safety_band("exercise", 80, True)[0] == "caution"
    assert compute_safety_band("exercise", 160, True)[0] == "avoid"
    assert compute_safety_band("commute", 210, False)[0] == "avoid"


def test_daily_routine_time_validation():
    with pytest.raises(ValidationError):
        DailyRoutineCreate(
            name="Morning Run",
            routine_type="exercise",
            start_time=time(9, 0),
            end_time=time(8, 0),
        )


def test_deterministic_recommendation_rules():
    missing_aqi = build_deterministic_rules(
        aqi_value=None,
        aqi_standard=None,
        location_name="Bengaluru",
        sensitivities=[],
        health_conditions=[],
    )
    assert any("sync local air quality" in r["title"].lower() for r in missing_aqi)

    high_aqi_sensitive = build_deterministic_rules(
        aqi_value=170,
        aqi_standard="US_AQI",
        location_name="Delhi",
        sensitivities=["Air pollution"],
        health_conditions=["Asthma"],
        temperature_c=36.0,
    )
    titles = " ".join(r["title"].lower() for r in high_aqi_sensitive)
    assert "indoors" in titles
    assert "10:00 am" in titles
