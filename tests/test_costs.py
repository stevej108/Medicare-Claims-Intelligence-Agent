import pytest
from pydantic import ValidationError

from tools.costs import (
    get_cost_concentration,
)


@pytest.mark.parametrize(
    "fraction, expected_share",
    [
        (0.01, 12.527900),
        (0.05, 34.673238),
        (0.10, 49.297037),
        (0.20, 66.153313),
    ],
)
def test_cost_concentration(
    fraction,
    expected_share,
):
    result = get_cost_concentration(
        fraction
    )

    assert result[
        "top_fraction"
    ] == fraction

    assert result[
        "spending_share_pct"
    ] == pytest.approx(
        expected_share,
        abs=0.01,
    )


@pytest.mark.parametrize(
    "invalid_fraction",
    [
        0,
        -0.10,
        1.01,
    ],
)
def test_invalid_cost_fraction(
    invalid_fraction,
):
    with pytest.raises(
        ValidationError
    ):
        get_cost_concentration(
            invalid_fraction
        )