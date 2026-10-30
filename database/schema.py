import duckdb


ANALYTICAL_VIEW = "analytical_member_year"


import duckdb


ANALYTICAL_VIEW = "analytical_member_year"


def register_analytical_views(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """
    Register the canonical analytical member-year view.

    Assumes these physical views already exist:
    - member_year
    - high_cost_persistence
    """

    connection.execute(
        f"""
        CREATE OR REPLACE VIEW {ANALYTICAL_VIEW} AS

        WITH base AS (

            SELECT
                m.*,

                h.high_cost_years,
                h.very_high_cost_years,
                h.mean_cost_percentile,
                h.high_cost_pattern,

                (
                    m.MEDREIMB_IP
                    + m.MEDREIMB_OP
                    + m.MEDREIMB_CAR
                    + m.rx_total_cost
                ) AS total_annual_cost,

                (m.inpatient_claims > 0)
                    AS has_inpatient_utilization,

                (
                    CASE WHEN m.SP_ALZHDMTA = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_CHF = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_CHRNKIDN = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_CNCR = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_COPD = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_DEPRESSN = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_DIABETES = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_ISCHMCHT = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_OSTEOPRS = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_RA_OA = 1 THEN 1 ELSE 0 END
                    + CASE WHEN m.SP_STRKETIA = 1 THEN 1 ELSE 0 END
                ) AS chronic_condition_count

            FROM member_year m

            LEFT JOIN high_cost_persistence h
                ON m.DESYNPUF_ID = h.DESYNPUF_ID
        ),

        thresholds AS (

            SELECT
                QUANTILE_CONT(
                    chronic_condition_count,
                    0.75
                ) AS chronic_p75,

                QUANTILE_CONT(
                    rx_days_supply,
                    0.90
                ) AS rx_days_p90,

                QUANTILE_CONT(
                    outpatient_claims,
                    0.90
                ) AS outpatient_p90,

                QUANTILE_CONT(
                    carrier_claims,
                    0.90
                ) AS carrier_p90

            FROM base
        ),

        ranked AS (

            SELECT
                base.*,

                PERCENT_RANK() OVER (
                    PARTITION BY year
                    ORDER BY total_annual_cost
                ) AS annual_cost_percentile,

                thresholds.chronic_p75,
                thresholds.rx_days_p90,
                thresholds.outpatient_p90,
                thresholds.carrier_p90

            FROM base

            CROSS JOIN thresholds
        )

        SELECT
            *,

            CASE

                WHEN
                    high_cost_pattern = 'Persistent high cost'
                    AND chronic_condition_count >= chronic_p75
                THEN 'Persistent high-cost complex'

                WHEN
                    high_cost_pattern = 'Recurrent high cost'
                    AND chronic_condition_count >= chronic_p75
                THEN 'Recurrent high-cost complex'

                WHEN
                    high_cost_pattern = 'Episodic high cost'
                    AND annual_cost_percentile >= 0.90
                    AND has_inpatient_utilization
                THEN 'Acute episodic high cost'

                WHEN
                    chronic_condition_count >= chronic_p75
                    AND rx_days_supply >= rx_days_p90
                    AND NOT has_inpatient_utilization
                THEN 'Pharmacy-intensive chronic'

                WHEN
                    NOT has_inpatient_utilization
                    AND (
                        outpatient_claims >= outpatient_p90
                        OR carrier_claims >= carrier_p90
                    )
                THEN 'High routine utilization'

                ELSE 'Stable / lower utilization'

            END AS member_segment

        FROM ranked
        """
    )