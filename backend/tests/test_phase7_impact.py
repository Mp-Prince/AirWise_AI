"""Unit tests for Phase 7 (Environmental Impact Engine & Emission Factors)."""
from datetime import date, timedelta

from app.modules.emission_factors.service import DEFAULT_EMISSION_FACTORS
from app.modules.impact_records.service import (
    IMPACT_DISCLAIMER,
    calculate_co2e_impact,
    compute_active_streak,
)


def test_reproducible_transport_and_electricity_calculations():
    # 10 km petrol car (0.171) -> metro rail (0.028)
    base, alt, saved = calculate_co2e_impact(10.0, 0.1710, 0.0280, passengers=1)
    assert base == 1.71
    assert alt == 0.28
    assert saved == 1.43

    # Carpooling 10 km in petrol car with 2 passengers
    base2, alt2, saved2 = calculate_co2e_impact(10.0, 0.1710, 0.1710, passengers=2)
    assert base2 == 1.71
    assert alt2 == 0.855
    assert saved2 == 0.855

    # Electricity saving 5 kWh at 0.716 kgCO2e/kWh
    ebase, ealt, esaved = calculate_co2e_impact(5.0, 0.7160, 0.0, activity_category="electricity")
    assert ebase == 3.58
    assert ealt == 0.0
    assert esaved == 3.58


def test_active_streak_calculation():
    today = date(2026, 11, 28)
    dates = {today, today - timedelta(days=1), today - timedelta(days=2), today - timedelta(days=5)}
    assert compute_active_streak(dates, reference_date=today) == 3
    assert compute_active_streak(set(), reference_date=today) == 0


def test_default_factors_and_honest_disclaimer():
    by_name = {f["activity"]: f for f in DEFAULT_EMISSION_FACTORS}
    assert by_name["bicycle"]["co2e_kg_per_unit"] == 0.0
    assert by_name["walking"]["co2e_kg_per_unit"] == 0.0
    assert all(f["source"] and f["unit"] for f in DEFAULT_EMISSION_FACTORS)
    assert "estimated" in IMPACT_DISCLAIMER.lower()
    assert "no personal pm2.5 reduction" in IMPACT_DISCLAIMER.lower()
