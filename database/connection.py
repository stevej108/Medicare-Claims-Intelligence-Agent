from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MEMBER_YEAR_PATH = (
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


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Return an in-memory DuckDB connection.
    """
    return duckdb.connect()


def register_member_year(
    connection: duckdb.DuckDBPyConnection,
    path: Path = MEMBER_YEAR_PATH,
) -> None:
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW member_year AS
        SELECT *
        FROM read_parquet('{path.as_posix()}')
        """
    )


def register_high_cost_persistence(
    connection: duckdb.DuckDBPyConnection,
    path: Path = PERSISTENCE_PATH,
) -> None:
    connection.execute(
        f"""
        CREATE OR REPLACE VIEW high_cost_persistence AS
        SELECT *
        FROM read_parquet('{path.as_posix()}')
        """
    )


def get_analytical_connection(
    member_year_path: Path = MEMBER_YEAR_PATH,
    persistence_path: Path = PERSISTENCE_PATH,
) -> duckdb.DuckDBPyConnection:
    con = get_connection()

    register_member_year(
        con,
        member_year_path,
    )

    register_high_cost_persistence(
        con,
        persistence_path,
    )

    from database.schema import register_analytical_views

    register_analytical_views(con)

    return con