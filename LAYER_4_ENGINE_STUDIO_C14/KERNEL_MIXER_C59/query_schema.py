
"""Expose the current public SQL table shapes for Workbench autocomplete."""

from __future__ import annotations

from typing import Any

from .graph_store import quote_identifier
from .header_columns import HeaderSchema
from .audit_tables import TABLES as AUDIT_TABLES
from .archive_catalog import ARCHIVE_ROLE_MAX, ARCHIVE_VERSION_MAX
from .boundary_tables import BOUNDARY_TABLES


def public_schema(connection: Any, header_schema: HeaderSchema) -> dict[str, dict[str, list[dict[str, Any]]]]:
    tables: dict[str, list[dict[str, Any]]] = {}
    for name in ("atoms", "scope_units", "relations", "change_log", "query_log", "live_runs", "runtime_diagnostics",
                 "implementation_objects", "implementation_rmedo", "import_nodes", "module_imports", "import_edges", "package_imports", "package_external_imports", "test_edges", "tested_by_edges", "import_read_issues", ARCHIVE_VERSION_MAX, ARCHIVE_ROLE_MAX, "atom_version_max",
                 *AUDIT_TABLES, "native_references",
                 "components", "component_metrics", "package_audit", *BOUNDARY_TABLES):
        rows = connection.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_catalog = current_database() AND table_schema = 'main' "
            "AND table_name = ? ORDER BY ordinal_position", [name],
        ).fetchall()
        if rows:
            tables[name] = [{"name": column, "type": data_type} for column, data_type in rows]
    for name in header_schema.status_names:
        values = [
            value[0]
            for value in connection.execute(
                f"SELECT DISTINCT {quote_identifier(name)} FROM main.atoms "
                f"WHERE {quote_identifier(name)} IS NOT NULL ORDER BY {quote_identifier(name)}"
            ).fetchall()
        ]
        if values:
            next(column for column in tables["atoms"] if column["name"] == name)["values"] = values
    return {"tables": tables}
