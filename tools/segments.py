from core.models import SegmentName
from database.connection import (
    get_analytical_connection,
)


def get_segment_profile(
    segment: SegmentName,
) -> dict:
    """
    Return the utilization, cost, and clinical profile
    of one validated member segment.
    """

    if not isinstance(segment, SegmentName):
        raise TypeError(
            "segment must be a SegmentName value."
        )

    con = get_analytical_connection()

    try:
        query = """
        SELECT
            COUNT(*) AS member_years,

            COUNT(
                DISTINCT DESYNPUF_ID
            ) AS unique_beneficiaries,

            AVG(
                total_annual_cost
            ) AS mean_annual_cost,

            AVG(
                chronic_condition_count
            ) AS mean_conditions,

            AVG(
                CASE
                    WHEN has_inpatient_utilization
                    THEN 1.0
                    ELSE 0.0
                END
            ) * 100
                AS inpatient_prevalence_pct,

            AVG(
                inpatient_days
            ) AS mean_inpatient_days,

            AVG(
                outpatient_claims
            ) AS mean_outpatient_claims,

            AVG(
                carrier_claims
            ) AS mean_carrier_claims,

            AVG(
                rx_events
            ) AS mean_rx_events,

            AVG(
                rx_days_supply
            ) AS mean_rx_days_supply

        FROM analytical_member_year

        WHERE member_segment = ?
        """

        row = con.execute(
            query,
            [segment.value],
        ).fetchone()

        columns = [
            "member_years",
            "unique_beneficiaries",
            "mean_annual_cost",
            "mean_conditions",
            "inpatient_prevalence_pct",
            "mean_inpatient_days",
            "mean_outpatient_claims",
            "mean_carrier_claims",
            "mean_rx_events",
            "mean_rx_days_supply",
        ]

        result = dict(zip(columns, row))

        if result["member_years"] == 0:
            raise ValueError(
                f"No data found for segment: "
                f"{segment.value}"
            )

        return {
            "segment": segment.value,
            **result,
        }

    finally:
        con.close()


def compare_segments(
    segment_a: SegmentName,
    segment_b: SegmentName,
) -> dict:
    """
    Compare two validated member segments across canonical
    utilization, cost, and clinical metrics.
    """

    if not isinstance(segment_a, SegmentName):
        raise TypeError(
            "segment_a must be a SegmentName value."
        )

    if not isinstance(segment_b, SegmentName):
        raise TypeError(
            "segment_b must be a SegmentName value."
        )

    if segment_a == segment_b:
        raise ValueError(
            "segment_a and segment_b must be different."
        )

    profile_a = get_segment_profile(segment_a)
    profile_b = get_segment_profile(segment_b)

    comparison_metrics = [
        "mean_annual_cost",
        "mean_conditions",
        "inpatient_prevalence_pct",
        "mean_inpatient_days",
        "mean_outpatient_claims",
        "mean_carrier_claims",
        "mean_rx_events",
        "mean_rx_days_supply",
    ]

    differences = {}

    for metric in comparison_metrics:
        value_a = profile_a[metric]
        value_b = profile_b[metric]

        difference = value_a - value_b

        if difference > 0:
            higher_segment = segment_a.value
        elif difference < 0:
            higher_segment = segment_b.value
        else:
            higher_segment = None

        differences[metric] = {
            "segment_a_value": value_a,
            "segment_b_value": value_b,
            "absolute_difference": difference,
            "higher_segment": higher_segment,
        }

    return {
        "segment_a": profile_a,
        "segment_b": profile_b,
        "differences": differences,
    }        