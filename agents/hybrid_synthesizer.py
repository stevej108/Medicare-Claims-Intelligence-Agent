import json

from core.llm import get_llm
from prompts.hybrid_synthesis import (
    HYBRID_SYNTHESIS_PROMPT,
)


def synthesize_hybrid_answer(
    question: str,
    analytical_result: dict,
    knowledge_result: dict,
) -> str:
    """
    Synthesize an answer using both structured analytics
    and retrieved methodological knowledge.
    """

    llm = get_llm()

    prompt = f"""
{HYBRID_SYNTHESIS_PROMPT}

User question:
{question}

Validated analytical evidence:
{json.dumps(
    analytical_result,
    indent=2,
    default=str,
)}

Retrieved knowledge evidence:
{json.dumps(
    knowledge_result,
    indent=2,
    default=str,
)}

Answer using only this evidence.
"""

    response = llm.invoke(prompt)

    return response.content.strip()