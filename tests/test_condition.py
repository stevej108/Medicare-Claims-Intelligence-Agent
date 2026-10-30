import pytest
from pydantic import ValidationError



from tools.conditions import (
    get_condition_prevalence,
)

from core.models import SegmentName


def test_condition_prevalence():
    result = get_condition_prevalence(
        SegmentName.PERSISTENT_COMPLEX
    )

    assert result["segment"] == (
        SegmentName.PERSISTENT_COMPLEX.value
    )

    assert result["member_years"] == 3_895

    assert len(result["conditions"]) == 11

    prevalences = [
        item["prevalence_pct"]
        for item in result["conditions"]
    ]

    assert all(
        0 <= value <= 100
        for value in prevalences
    )

    assert prevalences == sorted(
        prevalences,
        reverse=True,
    )


import pytest


def test_invalid_condition_segment():
    with pytest.raises(TypeError):
        get_condition_prevalence(
            "Persistent high-cost complex"
        )    