"""Publish the optional Realization Graph projection on the Workbench connection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .graph_store import register_graph

if TYPE_CHECKING:
    from .query_store import QueryStore


def _exists(connection, name):
    return bool(connection.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_schema = 'main' AND table_name = ?", [name],
    ).fetchone()[0])


def replace_imports(connection, graph, nodes, occurrences, edges, test_edges, sources=None, *, mark_graph_changed=None) -> None:
    """Replace a realization snapshot within the caller's transaction."""
    needs_registration = not _exists(connection, "test_edges")
    if not _exists(connection, "import_nodes"):
        connection.execute(
            "CREATE TABLE main.import_nodes (node_key VARCHAR PRIMARY KEY, kind VARCHAR NOT NULL, "
            "language VARCHAR, relative_path VARCHAR, scan_status VARCHAR, package_key VARCHAR)"
        )
        connection.execute(
            "CREATE TABLE main.module_imports (occurrence_key VARCHAR PRIMARY KEY, source_key VARCHAR NOT NULL, "
            'target_key VARCHAR, written_specifier VARCHAR NOT NULL, line BIGINT, "column" BIGINT, '
            "resolution_status VARCHAR NOT NULL, type_only BOOLEAN NOT NULL)"
        )
        connection.execute(
            "CREATE TABLE main.import_edges (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, "
            "occurrence_key VARCHAR NOT NULL, derived BOOLEAN NOT NULL, "
            "PRIMARY KEY (source_key, target_key, occurrence_key))"
        )
        connection.execute(
            "CREATE VIEW main.package_imports AS SELECT e.source_key, e.target_key, "
            "count(DISTINCT e.occurrence_key) AS occurrence_count FROM main.import_edges e "
            "JOIN main.import_nodes s ON e.source_key = s.node_key "
            "JOIN main.import_nodes t ON e.target_key = t.node_key "
            "WHERE s.kind = 'package' AND t.kind = 'package' "
            "GROUP BY e.source_key, e.target_key"
        )
    for table in ("test_edges", "tested_by_edges"):
        if not _exists(connection, table):
            connection.execute(
                f"CREATE TABLE main.{table} (source_key VARCHAR NOT NULL, target_key VARCHAR NOT NULL, "
                "PRIMARY KEY (source_key, target_key))"
            )
    if not _exists(connection, "import_read_issues"):
        connection.execute("CREATE TABLE main.import_read_issues "
                           "(relative_path VARCHAR PRIMARY KEY, error_message VARCHAR NOT NULL)")
    if not connection.execute(
        "SELECT 1 FROM information_schema.columns WHERE table_schema = 'main' "
        "AND table_name = 'import_nodes' AND column_name = 'package_type'"
    ).fetchone():
        connection.execute("ALTER TABLE main.import_nodes ADD COLUMN package_type VARCHAR")
        needs_registration = True
    test_keys = {source for source, _ in test_edges}
    typed_nodes = [(*node, "Test Package" if node[0] in test_keys else None) for node in nodes]
    for table, rows in (
        ("import_edges", edges), ("module_imports", occurrences), ("test_edges", test_edges),
        ("tested_by_edges", [(target, source) for source, target in test_edges]), ("import_nodes", typed_nodes),
        ("import_read_issues", [(path, source.error_message) for path, source in (sources or {}).items()
                                if source.status == "read_error" and source.error_message is not None]),
    ):
        connection.execute(f"DELETE FROM main.{table}")
        if rows:
            columns = [list(column) for column in zip(*rows, strict=True)]
            operands = ", ".join("unnest(?)" for _ in columns)
            connection.execute(f"INSERT INTO main.{table} SELECT {operands}", columns)
    if needs_registration:
        if mark_graph_changed is not None:
            mark_graph_changed()
        connection.execute("DROP PROPERTY GRAPH anechoic")
        register_graph(connection, graph)


def remove_imports(connection, graph, *, mark_graph_changed=None) -> None:
    """Remove the realization snapshot within the caller's transaction."""
    if not _exists(connection, "import_nodes"):
        return
    if mark_graph_changed is not None:
        mark_graph_changed()
    connection.execute("DROP PROPERTY GRAPH anechoic")
    connection.execute("DROP VIEW IF EXISTS main.package_imports")
    for table in ("test_edges", "tested_by_edges", "import_edges", "module_imports", "import_nodes", "import_read_issues"):
        connection.execute(f"DROP TABLE IF EXISTS main.{table}")
    register_graph(connection, graph)


def publish_imports(store: QueryStore, nodes, occurrences, edges) -> None:
    """Replace one complete import snapshot atomically."""
    with store._lock:
        connection = store._connection
        if store._projection is None:
            raise RuntimeError("Atom projection must exist before publishing imports")
        connection.execute("BEGIN TRANSACTION")
        try:
            replace_imports(connection, store._projection.graph, nodes, occurrences, edges, [])
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
