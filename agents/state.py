from typing import Any, TypedDict

from core.models import (
    HybridPlan,
    ToolRoute,
)


class ClaimsAgentState(TypedDict):
    question: str

    plan: HybridPlan | None
    mode: str | None

    analytical_route: ToolRoute | None
    analytical_result: dict[str, Any] | None

    knowledge_query: str | None
    knowledge_result: dict[str, Any] | None

    answer: str | None
    sources: list[str]
