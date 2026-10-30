from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEMBER_YEAR_PATH=(
    PROJECT_ROOT
    / "data"
    / "processed"
    / "member_year.parquet"
)

PERSISTENCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "high_cost_persistence.parquet"
)


def register_high_cost_persistence(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """
    Create a DuckDB view over the beneficiary-level
    high-cost persistence Parquet file.
    """

    connection.execute(
        f"""
        CREATE OR REPLACE VIEW high_cost_persistence AS
        SELECT *
        FROM read_parquet(
            '{PERSISTENCE_PATH.as_posix()}'
        )
        """
    )

def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Return an in-memory DuckDB connection.
    """
    return duckdb.connect()


def register_member_year(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    """
    Create a DuckDB view over the member-year Parquet file.

    DuckDB reads the Parquet file directly rather than
    loading the full dataset into a pandas DataFrame.
    """

    connection.execute(
        f"""
        CREATE OR REPLACE VIEW member_year AS
        SELECT *
        FROM read_parquet('{MEMBER_YEAR_PATH.as_posix()}')
        """
    )

def get_analytical_connection() -> duckdb.DuckDBPyConnection:
    """
    Return a DuckDB connection with all physical and
    analytical views registered.
    """

    con = get_connection()

    register_member_year(con)
    register_high_cost_persistence(con)

    # Local import avoids circular-import problems
    # if schema.py imports connection-related objects.
    from database.schema import register_analytical_views

    register_analytical_views(con)

    return con    