"""Publish the optional Realization Graph projection on the Workbench connection."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from .graph_store import register_graph

if TYPE_CHECKING:
    from .query_store import QueryStore


def _exists(connection, name):
    return bool(connection.execute(
        "SELECT count(*) FROM information_schema.tables "
        "WHERE table_catalog = current_database() AND table_schema = 'main' AND table_name = ?", [name],
    ).fetchone()[0])


def _create_external_imports_view(connection):
    stdlib = ", ".join("'" + name.replace("'", "''") + "'"
                       for name in sorted(sys.stdlib_module_names | set(sys.builtin_module_names)))
    connection.execute(
        "CREATE OR REPLACE VIEW main.package_external_imports AS "
        "SELECT p.relative_path AS package_path, s.language, "
        "split_part(t.node_key, ':', 3) AS import_name, count(*) AS occurrence_count, "
        "count(*) FILTER (WHERE i.type_only) AS type_only_count "
        "FROM main.module_imports i "
        "JOIN main.import_nodes s ON s.node_key = i.source_key "
        "JOIN main.import_nodes p ON p.node_key = s.package_key "
        "JOIN main.import_nodes t ON t.node_key = i.target_key "
        "WHERE s.kind = 'module' "
        "AND p.kind = 'package' AND p.relative_path IS NOT NULL "
        "AND i.resolution_status = 'external' AND t.node_key LIKE '%:external:%' "
        "AND (s.language <> 'python' OR split_part(t.node_key, ':', 3) NOT IN (" + stdlib + ")) "
        "GROUP BY p.relative_path, s.language, split_part(t.node_key, ':', 3)"
    )


def replace_imports(connection, graph, nodes, occurrences, edges, test_edges, sources=None, *, test_keys=None, mark_graph_changed=None) -> None:
    """Replace a realization snapshot within the caller's transaction."""
    needs_registration = _prepare_import_tables(connection)
    if test_keys is None:
        test_keys = {source for source, _ in test_edges}
    _replace_test_edges(connection, graph, nodes, test_edges)
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


def _prepare_import_tables(connection):
    needs_registration = not _exists(connection, "test_edges")
    _ensure_import_nodes(connection)
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
        "SELECT 1 FROM information_schema.columns WHERE table_catalog = current_database() AND table_schema = 'main' "
        "AND table_name = 'import_nodes' AND column_name = 'package_type'"
    ).fetchone():
        connection.execute("ALTER TABLE main.import_nodes ADD COLUMN package_type VARCHAR")
        needs_registration = True
    if not connection.execute("SELECT 1 FROM information_schema.tables WHERE table_catalog = current_database() AND table_schema = 'realization_internal' AND table_name = 'package_tests'").fetchone():
        connection.execute("CREATE SCHEMA IF NOT EXISTS realization_internal")
        for table in ("package_tests", "package_tested_by"):
            connection.execute(f"CREATE TABLE realization_internal.{table} (source_key VARCHAR, target_key VARCHAR)")
        connection.execute("CREATE TABLE realization_internal.component_tests (source_key VARCHAR, target_kind VARCHAR, target_key VARCHAR)")
        connection.execute("CREATE TABLE realization_internal.component_tested_by (source_kind VARCHAR, source_key VARCHAR, target_key VARCHAR)")
        needs_registration = True
    return needs_registration


def _ensure_import_nodes(connection):
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
    _create_external_imports_view(connection)


def _replace_test_edges(connection, graph, nodes, test_edges):
    package_keys = {node[0] for node in nodes if node[1] == "package"}
    package_tests = [(source, target) for source, target in test_edges if target in package_keys]
    component_tests = [(source, target) for source, target in test_edges if target not in package_keys]
    for _, target in component_tests:
        if ("Component", target) not in graph.references:
            raise ValueError(f"Missing Component test endpoint: {target}")
    for table, rows in (("package_tests", package_tests),
                        ("package_tested_by", [(target, source) for source, target in package_tests]),
                        ("component_tests", [(source, "Component", target) for source, target in component_tests]),
                        ("component_tested_by", [("Component", target, source) for source, target in component_tests])):
        connection.execute(f"DELETE FROM realization_internal.{table}")
        if rows:
            placeholders = ", ".join("?" for _ in rows[0])
            connection.executemany(f"INSERT INTO realization_internal.{table} VALUES ({placeholders})", rows)


def remove_imports(connection, graph, *, mark_graph_changed=None) -> None:
    """Remove the realization snapshot within the caller's transaction."""
    connection.execute("DROP VIEW IF EXISTS main.package_external_imports")
    if not _exists(connection, "import_nodes"):
        return
    if mark_graph_changed is not None:
        mark_graph_changed()
    connection.execute("DROP PROPERTY GRAPH anechoic")
    connection.execute("DROP SCHEMA IF EXISTS realization_internal CASCADE")
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
