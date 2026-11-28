"""Validate and write admitted Archive rows."""

from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.ingestion_issues import archive_path, duplicate_dependencies
from KERNEL_MIXER_beta_C67.DATABASE_SERVER_beta_C71.realization_support.delta.delta__shared import DeltaReconciliationRequired


def _validate_archive_issues(connection, snapshot):
    paths = [
        row["relative_path"] for row in snapshot.get("ingestion_issues", [])
    ]
    if (
        paths
        and connection.execute(
            """SELECT 1 FROM main.mrt_atom_references
            WHERE concat(CASE WHEN relative_path = '.' THEN '' ELSE
                relative_path || '/' END, filename)
            IN (SELECT unnest(?)) LIMIT 1""",
            [paths],
        ).fetchone()
    ):
        raise ValueError("Archive issue path collides with an admitted Atom")


def _check_archive_duplicates(connection, snapshot):
    excluded = [
        row["atom_ref"]
        for row in snapshot.get("ingestion_issues", [])
        if row["code"] == "duplicate_revision"
    ]
    collision = connection.execute(
        """SELECT 1 FROM main.mrt_atom_references n
        JOIN int_admission_atoms a USING (reference)
        UNION ALL SELECT 1 FROM main.mrt_atom_references n JOIN
            int_admission_atoms a USING (exact_ref)
        UNION ALL SELECT 1 FROM main.mrt_atom_references n
        WHERE exact_ref IN (SELECT unnest(?::VARCHAR[])) LIMIT 1""",
        [excluded],
    ).fetchone()
    if collision or duplicate_dependencies(connection, snapshot, set()):
        raise DeltaReconciliationRequired(
            "Archive Atom collides with another Atom phase"
        )


def _insert_edges(connection, edges):
    connection.execute(
        """INSERT INTO main.mrt_atom_graph_relations
        SELECT e.source_kind, e.source_ref, e.target_kind, e.target_ref,
            e.relation_type, e.derived
        FROM UNNEST(?::STRUCT(source_kind VARCHAR, source_ref VARCHAR,
            target_kind VARCHAR,
            target_ref VARCHAR, relation_type VARCHAR, derived BOOLEAN)[]) AS
                t(e)""",
        [edges],
    )


def _remove_canonical_archive(connection):
    connection.execute("""CREATE TEMP TABLE int_archive_replaced AS
        SELECT relative_path, filename, reference FROM main.mrt_atom_references
        WHERE status_group = 'Archived' AND
            list_contains(string_split(relative_path, '/'), '09_archived')""")
    connection.execute("""DELETE FROM main.mrt_atom_graph_relations
        WHERE (NOT derived AND source_kind = 'Atom' AND source_ref IN (SELECT
            reference FROM int_archive_replaced))
        OR (derived AND target_kind = 'Atom' AND target_ref IN (SELECT
            reference FROM int_archive_replaced))""")
    for table in ("mrt_atoms", "mrt_atom_references"):
        connection.execute(f"""DELETE FROM main.{table}
            WHERE (relative_path, filename) IN (
                SELECT relative_path, filename FROM int_archive_replaced)""")
    connection.execute("DROP TABLE int_archive_replaced")


def _check_replacement_paths(replacing, atoms, snapshot):
    if replacing and any(
        "09_archived" not in a.relative_path.split("/") for a in atoms
    ):
        raise ValueError(
            "Archive replacement requires canonical archive paths"
        )
    paths = [
        row["relative_path"] for row in snapshot.get("ingestion_issues", [])
    ]
    if replacing and any(not archive_path(path) for path in paths):
        raise ValueError(
            "Archive replacement requires canonical archive issue paths"
        )


def _archive_fields():
    fields = {
        "instance_id",
        "base_generation",
        "snapshot",
        "snapshot_sha256",
        "carrier_hashes",
    }
    batch = (fields - {"snapshot", "carrier_hashes"}) | {"batch_artifact"}
    return (
        fields,
        fields | {"paths"},
        fields | {"replace"},
        batch,
        batch | {"replace"},
        {"instance_id", "base_generation", "unchanged"},
    )
