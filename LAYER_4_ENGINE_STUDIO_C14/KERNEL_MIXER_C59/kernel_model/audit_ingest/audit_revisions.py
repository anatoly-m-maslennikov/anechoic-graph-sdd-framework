"""Refresh duplicate Atom revision diagnostics."""

from pathlib import Path
from typing import Any


def affected(
    connection: Any, paths: tuple[str, ...], revision_query
) -> set[tuple[str, int]]:
    if not paths:
        return set()
    arguments = [
        [Path(path).parent.as_posix() for path in paths],
        [Path(path).name for path in paths],
    ]
    path_filter = (
        "(relative_path, filename) IN "
        "(SELECT unnest(?::VARCHAR[]), unnest(?::VARCHAR[]))"
    )
    previous = connection.execute(
        f"SELECT observed, try_cast(expected AS BIGINT) FROM "
        f"main.atom_duplicate_revision_issues "
        f"WHERE issue_category = 'duplicate_atom_revision' AND {path_filter}",
        arguments,
    ).fetchall()
    current = connection.execute(
        f"SELECT atom_id, version FROM ({revision_query(connection)}) WHERE "
        f"{path_filter}",
        arguments,
    ).fetchall()
    return {
        (identity, version)
        for identity, version in [*previous, *current]
        if identity is not None and version is not None
    }


def refresh(
    connection: Any, affected: set[tuple[str, int]] | None, revision_query
) -> None:
    if affected is not None and not affected:
        return
    arguments: list[Any] = []
    restriction = ""
    if affected is not None:
        keys = sorted(affected)
        arguments = [
            [identity for identity, _ in keys],
            [version for _, version in keys],
        ]
        connection.execute(
            "DELETE FROM main.atom_duplicate_revision_issues WHERE "
            "issue_category = 'duplicate_atom_revision' "
            "AND (observed, try_cast(expected AS BIGINT)) IN "
            "(SELECT unnest(?::VARCHAR[]), unnest(?::BIGINT[]))",
            arguments,
        )
        restriction = (
            "AND (atom_id, version) IN "
            "(SELECT unnest(?::VARCHAR[]), unnest(?::BIGINT[]))"
        )
    connection.execute(
        f"INSERT INTO main.atom_duplicate_revision_issues "
        f"WITH revisions AS ({revision_query(connection)}), collisions AS ("
        "SELECT atom_id, version FROM revisions "
        "WHERE regexp_full_match(atom_id, '.+-[A-Z]-[0-9]+') AND version > 0 "
        f"{restriction} GROUP BY atom_id, version HAVING count(*) > 1) "
        "SELECT revisions.reference, revisions.relative_path, "
        "revisions.filename, "
        "'duplicate_atom_revision', 'atom_id,version', revisions.atom_id, "
        "cast(revisions.version AS VARCHAR), 'Multiple Atom files share "
        "this Atom ID and Version.' "
        "FROM revisions JOIN collisions USING (atom_id, version)",
        arguments,
    )
