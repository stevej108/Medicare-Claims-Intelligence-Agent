from core.llm import get_llm
from prompts.tool_router import (
    TOOL_ROUTER_PROMPT,
)

import re

from core.models import (
    ToolName,
    ToolRoute,
    SegmentName,
    normalize_segment_text,
    resolve_segment_name
)




KNOWLEDGE_PATTERNS = [
    r"\bhow (?:is|are|was|were) .+ calculated\b",
    r"\bhow (?:is|are|was|were) .+ defined\b",
    r"\bhow (?:is|are|was|were) .+ constructed\b",
    r"\bhow was .+ built\b",
    r"\bwhat does .+ mean\b",
    r"\bdefinition of\b",
    r"\bmethodology\b",
    r"\blimitations?\b",
    r"\bcan .+ be generalized\b",
    r"\bgeneralized to\b",
]


def detect_knowledge_intent(
    question: str,
) -> bool:
    """
    Detect explicit definition, methodology,
    provenance, or limitation questions.
    """

    normalized = " ".join(
        question.lower().split()
    )

    return any(
        re.search(pattern, normalized)
        for pattern in KNOWLEDGE_PATTERNS
    )



def canonicalize_route(
    route: ToolRoute,
) -> ToolRoute:
    """
    Convert model-generated arguments to canonical
    analytical values.
    """

    arguments = dict(route.arguments)

    if route.tool in {
        ToolName.SEGMENT_PROFILE,
        ToolName.CONDITION_PREVALENCE,
    }:
        segment = resolve_segment_name(
            arguments["segment"]
        )

        arguments["segment"] = segment.value

    elif route.tool == ToolName.SEGMENT_COMPARISON:
        segment_a = resolve_segment_name(
            arguments["segment_a"]
        )

        segment_b = resolve_segment_name(
            arguments["segment_b"]
        )

        arguments["segment_a"] = segment_a.value
        arguments["segment_b"] = segment_b.value

    return ToolRoute(
        tool=route.tool,
        arguments=arguments,
    )

def route_question(
    question: str,
) -> ToolRoute:
    """
    Route a natural-language analyst question to one
    validated analytical tool.
    """

    if not question.strip():
        raise ValueError(
            "question cannot be empty."
        )

    # Explicit definitions, methodology, provenance,
    # and limitation questions use RAG.
    if detect_knowledge_intent(question):
        return ToolRoute(
            tool=ToolName.KNOWLEDGE_SEARCH,
            arguments={
                "query": question.strip(),
            },
        )

    # Explicit requests to describe the observed profile
    # of one recognized segment use DuckDB.
    profile_segment = (
        detect_segment_profile_intent(
            question
        )
    )

    if profile_segment is not None:
        return ToolRoute(
            tool=ToolName.SEGMENT_PROFILE,
            arguments={
                "segment": profile_segment.value,
            },
        )

    # Remaining ambiguous analytical questions go to Qwen.
    llm = get_llm()

    structured_llm = (
        llm.with_structured_output(
            ToolRoute
        )
    )

    prompt = f"""
{TOOL_ROUTER_PROMPT}

User question:

{question}
"""

    raw_route = structured_llm.invoke(
        prompt
    )

    return canonicalize_route(
        raw_route
    )

def find_segment_in_question(
    question: str,
) -> SegmentName | None:
    """
    Identify a canonical member segment mentioned
    within a longer natural-language question.
    """

    normalized_question = normalize_segment_text(
        question
    )

    for segment in SegmentName:
        normalized_segment = normalize_segment_text(
            segment.value
        )

        if normalized_segment in normalized_question:
            return segment

    return None

SEGMENT_PROFILE_PATTERNS = [
    r"^\s*describe\b",
    r"\bwhat does .+ look like\b",
    r"\btell me about\b",
    r"\bsummarize .+ (?:segment|cohort|population)\b",
]


def detect_segment_profile_intent(
    question: str,
) -> SegmentName | None:
    """
    Detect explicit requests to describe one
    recognized analytical segment.
    """

    normalized = " ".join(
        question.lower().split()
    )

    # Leave condition-specific questions for
    # get_condition_prevalence.
    if (
        "condition" in normalized
        or "conditions" in normalized
    ):
        return None

    matches_profile = any(
        re.search(pattern, normalized)
        for pattern in SEGMENT_PROFILE_PATTERNS
    )

    if not matches_profile:
        return None

    return find_segment_in_question(
        question
    )