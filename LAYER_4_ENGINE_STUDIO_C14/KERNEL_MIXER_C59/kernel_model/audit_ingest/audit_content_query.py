"""Read projected Content values for Atom audit."""

from pathlib import Path
from typing import Any


def query_content_rows(
    connection: Any, paths: set[str] | None
) -> dict[tuple[str, str], dict[str, Any]]:
    """Read actual projected values for only affected source paths."""
    if paths is not None and not paths:
        return {}
    names = [
        row[0]
        for row in connection.execute(
            "SELECT column_name FROM information_schema.columns WHERE "
            "table_catalog=current_database() "
            "AND table_schema='main' AND table_name='atoms'"
        ).fetchall()
        if row[0].startswith("content.")
    ]
    columns = ["relative_path", "filename", *names]
    sql = (
        "SELECT "
        + ", ".join('"' + c.replace('"', '""') + '"' for c in columns)
        + " FROM main.atoms WHERE status_group <> 'Archived'"
    )
    args = []
    if paths is not None:
        sql += (
            ' AND ("relative_path", filename) IN '
            "(SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[]))"
        )
        args = [
            [Path(p).parent.as_posix() for p in paths],
            [Path(p).name for p in paths],
        ]
    return {
        (row[0], row[1]): dict(zip(names, row[2:], strict=False))
        for row in connection.execute(sql, args).fetchall()
    }
