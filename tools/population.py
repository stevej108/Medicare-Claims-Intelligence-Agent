from database.connection import (
    get_analytical_connection,
)

from database.schema import (
    register_analytical_views,
)




def get_population_summary() -> dict:
    """
    Return high-level statistics for the analytical
    member-year population.
    """

    con = get_analytical_connection()

    try:
        
        register_analytical_views(con)

        query = """
       SELECT
            COUNT(*) AS member_years,
            COUNT(DISTINCT DESYNPUF_ID) AS unique_beneficiaries,
            MIN(year) AS first_year,
            MAX(year) AS last_year,

            AVG(total_annual_cost)
                AS mean_annual_cost,

            MEDIAN(total_annual_cost)
                AS median_annual_cost,

            AVG(
                CASE
                    WHEN has_inpatient_utilization
                    THEN 1.0
                    ELSE 0.0
                END
            ) * 100
                AS inpatient_prevalence_pct,

            AVG(
                CASE
                    WHEN has_outpatient_utilization
                    THEN 1.0
                    ELSE 0.0
                END
            ) * 100
                AS outpatient_prevalence_pct,

            AVG(
                CASE
                    WHEN has_carrier_utilization
                    THEN 1.0
                    ELSE 0.0
                END
            ) * 100
                AS carrier_prevalence_pct,

            AVG(
                CASE
                    WHEN has_rx_utilization
                    THEN 1.0
                    ELSE 0.0
                END
            ) * 100
                AS rx_prevalence_pct

        FROM analytical_member_year
        """

        row = con.execute(query).fetchone()

        columns = [
            "member_years",
            "unique_beneficiaries",
            "first_year",
            "last_year",
            "mean_annual_cost",
            "median_annual_cost",
            "inpatient_prevalence_pct",
            "outpatient_prevalence_pct",
            "carrier_prevalence_pct",
            "rx_prevalence_pct",
        ]

        result = dict(zip(columns, row))

        return result

    finally:
        con.close()


