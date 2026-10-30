import pytest

from core.models import (
    SegmentName,
    resolve_segment_name,
)


@pytest.mark.parametrize(
    "value",
    [
        "Acute episodic high cost",
        "Acute episodic high-cost",
        "acute episodic high cost",
        "  Acute   Episodic  High-Cost  ",
    ],
)
def test_resolve_acute_episodic_segment(
    value,
):
    result = resolve_segment_name(value)

    assert result == SegmentName.ACUTE_EPISODIC


def test_unknown_segment_fails():
    with pytest.raises(
        ValueError,
        match="Unknown member segment",
    ):
        resolve_segment_name(
            "Expensive members"
        )    