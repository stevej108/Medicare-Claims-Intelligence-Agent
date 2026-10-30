import pytest
from _pytest.python import CallSpec2


from core.models import SegmentName
from tools.segments import get_segment_profile, compare_segments



def test_persistent_complex_profile():
    result = get_segment_profile(
        SegmentName.PERSISTENT_COMPLEX
    )

    assert result["segment"] == (
        "Persistent high-cost complex"
    )

    assert result["member_years"] == 3_895

    assert result["mean_annual_cost"] == pytest.approx(
        29_925.566110,
        abs=0.01,
    )

    assert result["mean_conditions"] == pytest.approx(
        6.486264,
        abs=0.001,
    )

    assert result[
        "inpatient_prevalence_pct"
    ] == pytest.approx(
        71.964056,
        abs=0.001,
    )

    assert result[
        "mean_inpatient_days"
    ] == pytest.approx(
        9.242105,
        abs=0.001,
    )

    assert result[
        "mean_outpatient_claims"
    ] == pytest.approx(
        8.600513,
        abs=0.001,
    )

    assert result[
        "mean_carrier_claims"
    ] == pytest.approx(
        47.751220,
        abs=0.001,
    )

    assert result[
        "mean_rx_events"
    ] == pytest.approx(
        33.903209,
        abs=0.001,
    )

    assert result[
        "mean_rx_days_supply"
    ] == pytest.approx(
        1081.540436,
        abs=0.001,
    )


def test_pharmacy_intensive_profile():
    result = get_segment_profile(
        SegmentName.PHARMACY_INTENSIVE
    )

    assert result["segment"] == (
        "Pharmacy-intensive chronic"
    )

    assert result["member_years"] == 10_169

    assert result["mean_annual_cost"] == pytest.approx(
        7_727.750025,
        abs=0.01,
    )

    assert result["mean_conditions"] == pytest.approx(
        5.385879,
        abs=0.001,
    )

    assert result[
        "inpatient_prevalence_pct"
    ] == pytest.approx(
        0.0,
        abs=0.001,
    )

    assert result[
        "mean_rx_events"
    ] == pytest.approx(
        60.468679,
        abs=0.001,
    )

    assert result[
        "mean_rx_days_supply"
    ] == pytest.approx(
        2046.255286,
        abs=0.001,
    )    

def test_invalid_segment_type():
    with pytest.raises(TypeError):
        get_segment_profile(
            "Persistent high-cost complex"
        )    


def test_compare_persistent_and_pharmacy():
    result = compare_segments(
        SegmentName.PERSISTENT_COMPLEX,
        SegmentName.PHARMACY_INTENSIVE,
    )

    differences = result["differences"]

    assert (
        differences[
            "mean_annual_cost"
        ]["higher_segment"]
        == SegmentName.PERSISTENT_COMPLEX.value
    )

    assert (
        differences[
            "mean_inpatient_days"
        ]["higher_segment"]
        == SegmentName.PERSISTENT_COMPLEX.value
    )

    assert (
        differences[
            "mean_rx_events"
        ]["higher_segment"]
        == SegmentName.PHARMACY_INTENSIVE.value
    )

    assert (
        differences[
            "mean_rx_days_supply"
        ]["higher_segment"]
        == SegmentName.PHARMACY_INTENSIVE.value
    )        


def test_compare_same_segment_fails():
    with pytest.raises(ValueError):
        compare_segments(
            SegmentName.PERSISTENT_COMPLEX,
            SegmentName.PERSISTENT_COMPLEX,
        )


