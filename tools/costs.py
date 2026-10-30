from core.models import CostConcentrationInput
from database.connection import (
    get_analytical_connection,
)


def get_cost_concentration(
    top_fraction: float,
) -> dict:
    """
    Calculate the share of positive annual spending
    attributable to the highest-cost fraction of
    member-years.

    Parameters
    ----------
    top_fraction:
        Fraction of positive-cost member-years to include.
        For example, 0.10 represents the top 10%.
    """

    validated_input = CostConcentrationInput(
        top_fraction=top_fraction
    )

    top_fraction = validated_input.top_fraction

    con = get_analytical_connection()

    try:
        query = """
        WITH positive_cost AS (

            SELECT
                DESYNPUF_ID,
                year,
                total_annual_cost,

                ROW_NUMBER() OVER (
                    ORDER BY total_annual_cost DESC
                ) AS cost_rank,

                COUNT(*) OVER () AS positive_member_years,

                SUM(total_annual_cost) OVER ()
                    AS total_positive_spending

            FROM analytical_member_year

            WHERE total_annual_cost > 0
        ),

        selected AS (

            SELECT
                *,

                GREATEST(
                    1,
                    FLOOR(
                        positive_member_years * ?
                    )
                )::BIGINT AS selected_member_years

            FROM positive_cost
        )

        SELECT
            MAX(positive_member_years)
                AS positive_member_years,

            MAX(selected_member_years)
                AS selected_member_years,

            MAX(total_positive_spending)
                AS total_positive_spending,

            SUM(
                CASE
                    WHEN cost_rank <= selected_member_years
                    THEN total_annual_cost
                    ELSE 0
                END
            ) AS selected_spending

        FROM selected
        """

        row = con.execute(
            query,
            [top_fraction],
        ).fetchone()

        (
            positive_member_years,
            selected_member_years,
            total_positive_spending,
            selected_spending,
        ) = row

        spending_share_pct = (
            selected_spending
            / total_positive_spending
            * 100
        )

        return {
            "top_fraction": top_fraction,
            "top_percent": top_fraction * 100,
            "positive_member_years": (
                positive_member_years
            ),
            "selected_member_years": (
                selected_member_years
            ),
            "total_positive_spending": (
                total_positive_spending
            ),
            "selected_spending": (
                selected_spending
            ),
            "spending_share_pct": (
                spending_share_pct
            ),
        }

    finally:
        con.close()