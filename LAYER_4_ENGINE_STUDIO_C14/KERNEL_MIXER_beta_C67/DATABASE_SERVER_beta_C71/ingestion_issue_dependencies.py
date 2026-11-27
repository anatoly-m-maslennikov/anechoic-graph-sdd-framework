"""Track archive failures and duplicate ingestion dependencies."""


def clear_archive_failure(connection):
    connection.execute(
        (
            "DELETE FROM main.ops_ingestion_issues "
            "WHERE source = 'archive' AND "
            "relative_path IS NULL"
        )
    )


def duplicate_dependencies(connection, snapshot, paths):
    exact = {row["exact_ref"] for row in snapshot["atoms"]}
    current = {
        row["reference"]
        for row in snapshot["atoms"]
        if row["status_group"] == "Current"
    }
    duplicates = connection.execute(
        "SELECT relative_path, code, atom_ref, related_paths\n"
        "        FROM main.ops_ingestion_issues WHERE source IN "
        "('atom', 'archive')\n"
        "        AND code IN ('duplicate_revision', 'duplicate_current')"
    ).fetchall()
    return any(
        path in paths
        or not paths.isdisjoint(related)
        or ref in exact
        or code == "duplicate_current"
        and ref
        and ref.split("@", 1)[0] in current
        for path, code, ref, related in duplicates
    )
