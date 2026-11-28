"""Track Archive admission state and retained version maxima."""

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_projection import has_table


def archive_pending(connection):
    if not has_table(connection, "main", "ops_archive_state"):
        return False
    row = connection.execute(
        "SELECT pending FROM ops_archive_state"
    ).fetchone()
    return bool(row and row[0])


def refresh_archive_versions(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS main.ops_archive_versions
        (atom_id VARCHAR PRIMARY KEY, max_version BIGINT NOT NULL)""")
    connection.execute("DELETE FROM main.ops_archive_versions")
    connection.execute("""INSERT INTO main.ops_archive_versions
        SELECT split_part(reference, '@', 1), max("header.state.version")
        FROM main.mrt_atoms WHERE status_group = 'Archived' GROUP BY 1""")


def seed_archive_versions(connection, versions):
    if versions is None or has_table(
        connection, "main", "ops_archive_versions"
    ):
        return
    connection.execute("""CREATE TABLE main.ops_archive_versions
        (atom_id VARCHAR PRIMARY KEY, max_version BIGINT NOT NULL)""")
    if versions:
        connection.execute(
            """INSERT INTO main.ops_archive_versions
            SELECT unnest(?::VARCHAR[]), unnest(?::BIGINT[])""",
            [list(versions), list(versions.values())],
        )


def backfill_archive_versions(connection):
    if (
        not has_table(connection, "main", "ops_archive_versions")
        and not archive_pending(connection)
        and has_table(connection, "main", "mrt_atom_references")
    ):
        refresh_archive_versions(connection)


def update_archive_versions(connection, old, atoms):
    """Preserve admitted maxima until the full Archive history is available."""
    affected = {
        ref.partition("@")[0]
        for ref, _ in old
        if "@" in ref and not ref.endswith("-draft")
    }
    affected.update(
        row["reference"].partition("@")[0]
        for row in atoms
        if row["status_group"] == "Archived"
    )
    if not affected or not has_table(
        connection, "main", "ops_archive_versions"
    ):
        return
    if archive_pending(connection):
        connection.execute("""INSERT INTO main.ops_archive_versions
            SELECT split_part(reference, '@', 1), max("header.state.version")
            FROM int_admission_atoms WHERE status_group = 'Archived' GROUP BY 1
            ON CONFLICT (atom_id) DO UPDATE SET max_version =
                greatest(ops_archive_versions.max_version,
                excluded.max_version)""")
        return
    ids = [sorted(affected)]
    connection.execute(
        (
            "DELETE FROM main.ops_archive_versions WHERE atom_id IN (SELECT u"
            "nnest(?))"
        ),
        ids,
    )
    connection.execute(
        """INSERT INTO main.ops_archive_versions
        SELECT split_part(reference, '@', 1), max("header.state.version") FROM
            main.mrt_atoms
        WHERE status_group = 'Archived' AND split_part(reference, '@', 1) IN
            (SELECT unnest(?)) GROUP BY 1""",
        ids,
    )


def set_archive_pending(connection, pending):
    connection.execute(
        (
            "CREATE TABLE IF NOT EXISTS ops_archive_state (pending BOOLEAN NO"
            "T NULL)"
        )
    )
    connection.execute("DELETE FROM ops_archive_state")
    connection.execute("INSERT INTO ops_archive_state VALUES (?)", [pending])
