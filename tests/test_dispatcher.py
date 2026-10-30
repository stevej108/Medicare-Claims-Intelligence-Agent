import pytest

from agents.dispatcher import dispatch_tool
from core.models import (
    ToolName,
    ToolRoute,
)


def test_dispatch_population_summary():
    route = ToolRoute(
        tool=ToolName.POPULATION_SUMMARY,
        arguments={},
    )

    result = dispatch_tool(route)

    assert result["member_years"] == 343_644


def test_dispatch_cost_concentration():
    route = ToolRoute(
        tool=ToolName.COST_CONCENTRATION,
        arguments={
            "top_fraction": 0.10,
        },
    )

    result = dispatch_tool(route)

    assert result[
        "spending_share_pct"
    ] == pytest.approx(
        49.297037,
        abs=0.01,
    )


def test_dispatch_segment_profile():
    route = ToolRoute(
        tool=ToolName.SEGMENT_PROFILE,
        arguments={
            "segment": (
                "Persistent high-cost complex"
            ),
        },
    )

    result = dispatch_tool(route)

    assert result["member_years"] == 3_895


def test_dispatch_normalizes_segment_name():
    route = ToolRoute(
        tool=ToolName.SEGMENT_PROFILE,
        arguments={
            "segment": (
                "Acute episodic high-cost"
            ),
        },
    )

    result = dispatch_tool(route)

    assert result["segment"] == (
        "Acute episodic high cost"
    )    

def test_invalid_route_type():
    with pytest.raises(TypeError):
        dispatch_tool(
            {
                "tool": "get_population_summary",
                "arguments": {},
            }
        )    