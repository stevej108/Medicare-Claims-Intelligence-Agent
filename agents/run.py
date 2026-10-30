from typing import Any

from agents.dispatcher import dispatch_tool
from agents.router import route_question
from agents.synthesizer import synthesize_answer


def _extract_sources(
    tool_result: dict[str, Any],
) -> list[str]:
    """
    Extract unique knowledge-source filenames from a
    retrieval result.

    Analytical tools normally return no sources.
    """

    results = tool_result.get(
        "results",
        []
    )

    sources = []

    for result in results:
        source = result.get("source")

        if (
            source
            and source not in sources
        ):
            sources.append(source)

    return sources


def run_claims_agent(
    question: str,
) -> dict[str, Any]:
    """
    Execute the Medicare Claims Intelligence workflow.

    Steps:
    1. Route the user question.
    2. Execute the validated analytical or retrieval tool.
    3. Generate a grounded analyst-facing answer.
    4. Return response metadata for traceability.
    """

    if not question.strip():
        raise ValueError(
            "question cannot be empty."
        )

    route = route_question(
        question
    )

    tool_result = dispatch_tool(
        route
    )

    answer = synthesize_answer(
        question=question,
        route=route,
        tool_result=tool_result,
    )

    sources = _extract_sources(
        tool_result
    )

    return {
        "question": question,
        "answer": answer,
        "tool": route.tool.value,
        "arguments": route.arguments,
        "tool_result": tool_result,
        "sources": sources,
        "data_context": (
            "CMS DE-SynPUF synthetic Medicare data"
        ),
        "synthetic_data_notice": (
            "Results describe a synthetic analytical "
            "population and should not be interpreted "
            "as estimates for actual Medicare beneficiaries."
        ),
    }