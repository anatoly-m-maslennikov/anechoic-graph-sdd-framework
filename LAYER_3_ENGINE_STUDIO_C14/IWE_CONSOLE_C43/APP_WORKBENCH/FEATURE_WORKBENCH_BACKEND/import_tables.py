"""Publish the optional import projection on the Workbench connection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .graph_store import register_graph

if TYPE_CHECKING:
    from .query_store import QueryStore


def publish_imports(store: QueryStore, nodes, occurrences, edges) -> None:
    """Replace one complete import snapshot atomically."""
    with store._lock:
        connection = store._connection
        if store._projection is None:
            raise RuntimeError("Atom projection must exist before publishing imports")
        connection.execute("BEGIN TRANSACTION")
        try:
            exists = connection.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'main' AND table_name = 'import_nodes'"
            ).fetchone()[0]
            if not exists:
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
            for table, rows in (
                ("import_edges", edges), ("module_imports", occurrences), ("import_nodes", nodes),
            ):
                connection.execute(f"DELETE FROM main.{table}")
                if rows:
                    columns = [list(column) for column in zip(*rows, strict=True)]
                    operands = ", ".join("unnest(?)" for _ in columns)
                    connection.execute(f"INSERT INTO main.{table} SELECT {operands}", columns)
            if not exists:
                connection.execute("DROP PROPERTY GRAPH anechoic")
                register_graph(connection, store._projection.graph)
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
