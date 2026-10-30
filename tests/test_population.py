import pytest

from tools.population import get_population_summary


def test_population_summary():
    result = get_population_summary()

    assert result["member_years"] == 343_644

    assert result["inpatient_prevalence_pct"] == pytest.approx(
        13.504382,
        abs=0.001,
    )

    assert result["outpatient_prevalence_pct"] == pytest.approx(
        54.249747,
        abs=0.001,
    )

    assert result["carrier_prevalence_pct"] == pytest.approx(
        76.456158,
        abs=0.001,
    )

    assert result["rx_prevalence_pct"] == pytest.approx(
        71.537405,
        abs=0.001,
    )

    assert result["mean_annual_cost"] == pytest.approx(
        4605.670345,
        abs=0.01,
    )

    assert result["median_annual_cost"] == pytest.approx(
        1970.0,
        abs=0.01,
    )