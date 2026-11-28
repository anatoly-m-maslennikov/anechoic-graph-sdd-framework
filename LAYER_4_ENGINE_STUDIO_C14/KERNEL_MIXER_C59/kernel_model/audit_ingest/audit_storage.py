"""Create and update Atom audit tables in the caller's transaction."""

from pathlib import Path
from typing import Any, Mapping


PARSE_ISSUES = "atom_parse_issues"
SCHEMA_ISSUES = "atom_schema_issues"
DECLARED_CARRIER_ISSUES = "atom_declared_carrier_issues"
PHYSICAL_CARRIER_ISSUES = "atom_physical_carrier_issues"
TABLES = (
    PARSE_ISSUES,
    SCHEMA_ISSUES,
    DECLARED_CARRIER_ISSUES,
    PHYSICAL_CARRIER_ISSUES,
    "atom_duplicate_revision_issues",
)
COLUMNS = (
    "reference",
    "relative_path",
    "filename",
    "issue_category",
    "property",
    "observed",
    "expected",
    "diagnostic",
)


def create_tables(connection: Any, tables, columns) -> None:
    for table in tables:
        connection.execute(f"DROP TABLE IF EXISTS main.{table}")
        connection.execute(
            f"CREATE TABLE main.{table} "
            f"({', '.join(f'{name} VARCHAR' for name in columns)})"
        )


def clear(connection: Any, paths: tuple[str, ...] | None, tables) -> None:
    """Replace diagnostics for selected sources, or for all sources."""
    for table in tables:
        if paths is None:
            connection.execute(f"DELETE FROM main.{table}")
        elif paths:
            connection.execute(
                f"DELETE FROM main.{table} WHERE (relative_path, filename) IN "
                "(SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[]))",
                [
                    [Path(path).parent.as_posix() for path in paths],
                    [Path(path).name for path in paths],
                ],
            )


def insert(
    connection: Any,
    issues: Mapping[str, list[tuple[str | None, ...]]],
    tables,
    columns,
) -> None:
    for table in tables:
        rows = issues.get(table, [])
        if rows:
            connection.execute(
                f"INSERT INTO main.{table} SELECT "
                + ", ".join("unnest(?::VARCHAR[])" for _ in columns),
                [
                    [row[index] for row in rows]
                    for index in range(len(columns))
                ],
            )
