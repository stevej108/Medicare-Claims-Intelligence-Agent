from core.models import SegmentName
from database.connection import (
    get_analytical_connection,
)


CONDITION_LABELS = {
    "SP_ALZHDMTA": "Alzheimer's / Dementia",
    "SP_CHF": "Heart Failure",
    "SP_CHRNKIDN": "Chronic Kidney Disease",
    "SP_CNCR": "Cancer",
    "SP_COPD": "COPD",
    "SP_DEPRESSN": "Depression",
    "SP_DIABETES": "Diabetes",
    "SP_ISCHMCHT": "Ischemic Heart Disease",
    "SP_OSTEOPRS": "Osteoporosis",
    "SP_RA_OA": "Rheumatoid Arthritis / Osteoarthritis",
    "SP_STRKETIA": "Stroke / TIA",
}


def get_condition_prevalence(
    segment: SegmentName,
) -> dict:
    """
    Return chronic-condition prevalence for a validated
    member segment.
    """

    if not isinstance(segment, SegmentName):
        raise TypeError(
            "segment must be a SegmentName value."
        )

    con = get_analytical_connection()

    try:
        prevalence_expressions = []

        for column, label in CONDITION_LABELS.items():
            prevalence_expressions.append(
                f"""
                AVG(
                    CASE
                        WHEN {column} = 1
                        THEN 1.0
                        ELSE 0.0
                    END
                ) * 100 AS "{label}"
                """
            )

        prevalence_sql = ",\n".join(
            prevalence_expressions
        )

        query = f"""
        SELECT
            COUNT(*) AS member_years,
            {prevalence_sql}

        FROM analytical_member_year

        WHERE member_segment = ?
        """

        row = con.execute(
            query,
            [segment.value],
        ).fetchone()

        columns = [
            "member_years",
            *CONDITION_LABELS.values(),
        ]

        result = dict(
            zip(columns, row)
        )

        member_years = result.pop(
            "member_years"
        )

        condition_prevalence = [
            {
                "condition": condition,
                "prevalence_pct": prevalence,
            }
            for condition, prevalence
            in result.items()
        ]

        condition_prevalence.sort(
            key=lambda item: item[
                "prevalence_pct"
            ],
            reverse=True,
        )

        return {
            "segment": segment.value,
            "member_years": member_years,
            "conditions": condition_prevalence,
        }

    finally:
        con.close()