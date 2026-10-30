from enum import Enum
from pydantic import BaseModel, Field, model_validator


class SegmentName(str, Enum):
    PERSISTENT_COMPLEX = (
        "Persistent high-cost complex"
    )

    RECURRENT_COMPLEX = (
        "Recurrent high-cost complex"
    )

    ACUTE_EPISODIC = (
        "Acute episodic high cost"
    )

    PHARMACY_INTENSIVE = (
        "Pharmacy-intensive chronic"
    )

    HIGH_ROUTINE = (
        "High routine utilization"
    )

    STABLE_LOWER = (
        "Stable / lower utilization"
    )

import re


def normalize_segment_text(
    value: str,
) -> str:
    """
    Normalize segment text for alias matching.

    This removes differences in capitalization,
    punctuation, hyphens, and repeated whitespace.
    """

    normalized = value.lower().strip()

    normalized = re.sub(
        r"[-_/]+",
        " ",
        normalized,
    )

    normalized = re.sub(
        r"[^a-z0-9\s]",
        "",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized

def resolve_segment_name(
    value: str,
) -> SegmentName:
    """
    Resolve a model-generated segment name to its
    canonical SegmentName value.
    """

    if not isinstance(value, str):
        raise TypeError(
            "Segment value must be a string."
        )

    normalized_value = normalize_segment_text(
        value
    )

    for segment in SegmentName:
        if (
            normalize_segment_text(segment.value)
            == normalized_value
        ):
            return segment

    valid_values = [
        segment.value
        for segment in SegmentName
    ]

    raise ValueError(
        f"Unknown member segment: {value!r}. "
        f"Valid segments are: {valid_values}"
    )



from pydantic import BaseModel, Field


class CostConcentrationInput(BaseModel):
    top_fraction: float = Field(
        gt=0,
        le=1,
        description=(
            "Highest-cost fraction of positive-cost "
            "member-years to analyze."
        ),
    )    


class ToolName(str, Enum):
    POPULATION_SUMMARY = "get_population_summary"
    SEGMENT_PROFILE = "get_segment_profile"
    SEGMENT_COMPARISON = "compare_segments"
    COST_CONCENTRATION = "get_cost_concentration"
    CONDITION_PREVALENCE = "get_condition_prevalence"
    KNOWLEDGE_SEARCH = "knowledge_search"


class ToolRoute(BaseModel):
    tool: ToolName
    arguments: dict        


class AgentMode(str, Enum):
    ANALYTICS = "analytics"
    KNOWLEDGE = "knowledge"
    HYBRID = "hybrid"

class HybridPlan(BaseModel):
    mode: AgentMode

    analytical_question: str | None = None
    knowledge_query: str | None = None

    @model_validator(mode="after")
    def validate_plan(self):
        if self.mode == AgentMode.HYBRID:
            if not self.analytical_question:
                raise ValueError(
                    "Hybrid mode requires "
                    "analytical_question."
                )

            if not self.knowledge_query:
                raise ValueError(
                    "Hybrid mode requires "
                    "knowledge_query."
                )

        return self 

from typing import Any

from pydantic import BaseModel, Field


class ClaimsAgentResponse(BaseModel):
    question: str
    answer: str

    mode: AgentMode

    analytical_tool: str | None = None
    analytical_arguments: dict[str, Any] = Field(
        default_factory=dict
    )

    sources: list[str] = Field(
        default_factory=list
    )

    data_context: str = (
        "CMS DE-SynPUF synthetic Medicare data"
    )

    synthetic_data_notice: str = (
        "Results describe a synthetic analytical population "
        "and should not be interpreted as estimates for "
        "actual Medicare beneficiaries."
    )    
    
        