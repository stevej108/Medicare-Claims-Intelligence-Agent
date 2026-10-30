from typing import Any

from core.models import (
    SegmentName,
    ToolName,
    ToolRoute,
    resolve_segment_name,
)

from tools.conditions import (
    get_condition_prevalence,
)

from tools.costs import (
    get_cost_concentration,
)

from tools.population import (
    get_population_summary,
)

from tools.segments import (
    compare_segments,
    get_segment_profile,
)

from tools.knowledge import knowledge_search


def dispatch_tool(
    route: ToolRoute,
) -> dict[str, Any]:
    """
    Execute the validated analytical tool identified
    by a ToolRoute.

    The dispatcher forms the boundary between the
    probabilistic routing layer and deterministic
    analytical functions.
    """

    if not isinstance(route, ToolRoute):
        raise TypeError(
            "route must be a ToolRoute instance."
        )

    arguments = route.arguments

    if route.tool == ToolName.POPULATION_SUMMARY:
        return get_population_summary()

    if route.tool == ToolName.SEGMENT_PROFILE:
        segment = resolve_segment_name(
            arguments["segment"]
        )

        return get_segment_profile(
            segment
        )

    if route.tool == ToolName.SEGMENT_COMPARISON:
        segment_a = resolve_segment_name(
            arguments["segment_a"]
        )

        segment_b = resolve_segment_name(
            arguments["segment_b"]
        )

        return compare_segments(
            segment_a,
            segment_b,
        )

    if route.tool == ToolName.COST_CONCENTRATION:
        return get_cost_concentration(
            top_fraction=float(
                arguments["top_fraction"]
            )
        )

    if route.tool == ToolName.CONDITION_PREVALENCE:
        segment = resolve_segment_name(
            arguments["segment"]
        )

        return get_condition_prevalence(
            segment
        )

    if route.tool == ToolName.KNOWLEDGE_SEARCH:
            return knowledge_search(
                query=arguments["query"]
        )

    raise ValueError(
        f"Unsupported tool: {route.tool}"
    )

    