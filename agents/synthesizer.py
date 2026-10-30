import json
from typing import Any

from core.llm import get_llm
from core.models import ToolRoute
from prompts.synthesis import SYNTHESIS_PROMPT


def synthesize_answer(
    question: str,
    route: ToolRoute,
    tool_result: dict[str, Any],
) -> str:
    """
    Generate an analyst-facing explanation grounded only
    in the validated analytical tool result.
    """

    if not question.strip():
        raise ValueError(
            "question cannot be empty."
        )

    if not isinstance(route, ToolRoute):
        raise TypeError(
            "route must be a ToolRoute instance."
        )

    if not isinstance(tool_result, dict):
        raise TypeError(
            "tool_result must be a dictionary."
        )

    llm = get_llm()

    tool_result_json = json.dumps(
        tool_result,
        indent=2,
        default=str,
    )

    prompt = f"""
{SYNTHESIS_PROMPT}

User question:
{question}

Analytical tool used:
{route.tool.value}

Tool arguments:
{json.dumps(route.arguments, indent=2)}

Validated analytical result:
{tool_result_json}

Answer the user's question using only this evidence.
"""

    response = llm.invoke(prompt)

    return response.content.strip()