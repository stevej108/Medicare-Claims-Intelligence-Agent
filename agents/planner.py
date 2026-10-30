from core.llm import get_llm
from core.models import HybridPlan
from prompts.planner import (
    HYBRID_PLANNER_PROMPT,
)


def plan_question(
    question: str,
) -> HybridPlan:
    """
    Determine whether a question requires analytical
    evidence, knowledge retrieval, or both.
    """

    if not question.strip():
        raise ValueError(
            "question cannot be empty."
        )

    llm = get_llm()

    structured_llm = (
        llm.with_structured_output(
            HybridPlan
        )
    )

    prompt = f"""
{HYBRID_PLANNER_PROMPT}

User question:

{question}
"""

    return structured_llm.invoke(
        prompt
    )