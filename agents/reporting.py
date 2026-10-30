from core.models import (
    AgentMode,
    ClaimsAgentResponse,
)


def build_agent_response(
    state: dict,
) -> ClaimsAgentResponse:
    """
    Convert completed LangGraph state into the
    application-facing response contract.
    """

    route = state.get(
        "analytical_route"
    )

    analytical_tool = None
    analytical_arguments = {}

    if route is not None:
        analytical_tool = (
            route.tool.value
        )

        analytical_arguments = (
            route.arguments
        )

    return ClaimsAgentResponse(
        question=state["question"],
        answer=state["answer"],
        mode=AgentMode(
            state["mode"]
        ),
        analytical_tool=analytical_tool,
        analytical_arguments=(
            analytical_arguments
        ),
        sources=state.get(
            "sources",
            [],
        ),
    )