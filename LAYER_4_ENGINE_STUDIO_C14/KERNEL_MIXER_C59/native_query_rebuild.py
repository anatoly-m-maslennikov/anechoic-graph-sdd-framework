"""Native query projection rebuild operations."""
from __future__ import annotations

from contextlib import nullcontext
import re
import sys
from typing import Any

from .audit_tables import TABLES as AUDIT_TABLES, create_tables
from . import boundary_tables, realization_projection
from .import_cache import clear_import_sources
from .import_tables import remove_imports
from .query_store import QueryStore
from .spec_trace import remove_native_traces
from .watcher_change_log import mirror_change_log


ATOM_TABLES = frozenset(
    {
        "atoms",
        "relations",
        "native_references",
        "components",
    }
)
REALIZATION_TABLES = frozenset(
    {
        "import_nodes",
        "module_imports",
        "import_edges",
        "package_imports",
        "package_external_imports",
        "test_edges",
        "tested_by_edges",
        "import_read_issues",
        "implementation_rmedo",
        "component_metrics",
        "package_audit",
        *boundary_tables.BOUNDARY_TABLES,
    }
)
IMPORT_CACHE_TABLES = frozenset(
    f"_anechoic_import_cache.{name}"
    for name in ("sources", "sites", "version")
)
OBSERVATION_TABLES = frozenset(
    {"change_log", "query_log", "live_runs", "runtime_diagnostics"}
)
QUERY_TABLES = (
    ATOM_TABLES
    | REALIZATION_TABLES
    | OBSERVATION_TABLES
    | frozenset(AUDIT_TABLES)
    | {"work_journal"}
)


class NativeQueryRebuild:
    def _rebuild_observations(
        self, store: QueryStore, target: str, query_attempts
    ) -> None:
        connection = store._connection
        if target in ("all", "change_log"):
            mirror_change_log(
                connection,
                self._change_log,
                initialize=True,
                in_transaction=True,
            )
        if target in ("all", "query_log"):
            connection.execute("DELETE FROM main.query_log_records")
            store.record_query_attempts(query_attempts)
        if target in ("all", "live_runs"):
            connection.execute("DELETE FROM main.live_runs")
            if store._live_runs:
                connection.executemany(
                    "INSERT INTO main.live_runs VALUES (?, ?, ?, ?)",
                    store._live_runs,
                )
        if target in ("all", "runtime_diagnostics"):
            connection.execute("DELETE FROM main.runtime_diagnostics")
            if store._diagnostic_rows:
                connection.executemany(
                    "INSERT INTO main.runtime_diagnostics VALUES (?, ?, ?, ?, ?, ?, ?)",
                    store._diagnostic_rows,
                )
        if target == "all" or target in AUDIT_TABLES:
            create_tables(connection)

    def _rebuild_scope(
        self, store: QueryStore, target: str
    ) -> tuple[str, str, set[str] | None]:
        if not isinstance(target, str):
            raise ValueError(
                "Workbench rebuild target must be a table name or all"
            )
        table = target.removeprefix("main.")
        if table == "all":
            return table, "all", None
        if table == "workbench_results":
            return table, "results", None
        if re.fullmatch(r"(?:workbench_results\.)?(?:query_)?[a-f0-9]{32}", table):
            return table, "result", None
        atom_tables = ATOM_TABLES | {
            "scope_units",
            "internal.reference",
            "internal.native_exact_refs",
            "internal.native_frontier",
        }
        atom_tables |= {
            f"internal.{name[1:-1]}"
            for name in store._projection.graph.tables.values()
        }
        if table in atom_tables:
            return (
                table,
                "atoms",
                atom_tables
                | set(AUDIT_TABLES)
                | {"anechoic", "component_metrics", "package_audit"},
            )
        if table in REALIZATION_TABLES or table in IMPORT_CACHE_TABLES:
            if self._realization_options is None:
                raise ValueError("Realization Graph is disabled")
            return (
                table,
                "realization",
                set(REALIZATION_TABLES | IMPORT_CACHE_TABLES | {"anechoic"}),
            )
        if table in ("query_log_records", "query_log"):
            return "query_log", "observation", {"query_log", "query_log_records"}
        if table in OBSERVATION_TABLES or table in AUDIT_TABLES:
            return table, "observation", {table}
        raise ValueError(f"Unknown Workbench rebuild target: {target!r}")

    def rebuild(self, target: str) -> dict[str, Any]:
        """Rebuild the selected projection and dependent tables on the existing connection."""
        with self._interface_lock:
            staged = {}
            try:
                store = self._owner()
                table, scope, dependent_inputs = self._rebuild_scope(store, target)
                prepared = (self._prepare_realization(store, force_parse=scope == "all" or table in IMPORT_CACHE_TABLES)
                            if scope in ("all", "realization") and self._realization_options is not None else None)

                observations = self._query_log.snapshot() if table in ("all", "query_log") else nullcontext([])
                with observations as query_attempts, store._lock:
                    def rebuild_dependents(graph, capture) -> None:
                        nonlocal staged
                        bindings = None
                        if prepared is not None:
                            bindings = realization_projection.publish(store, graph, prepared)
                        elif scope == "all":
                            remove_imports(store._connection, graph,
                                           mark_graph_changed=store.mark_graph_registration_changed)
                            clear_import_sources(store._connection)
                            remove_native_traces(store._connection)
                        self._rebuild_observations(store, table, query_attempts)
                        if scope == "atoms":
                            create_tables(store._connection)
                        if scope in ("all", "atoms", "realization"):
                            self._publish_realization_metadata(
                                store, capture, bindings
                            )
                        staged = store.prepare_result_rebuild(
                            table if scope == "result" else None,
                            tables=dependent_inputs,
                        )

                    if scope in ("all", "atoms"):
                        self._capture = self._project(store, before_commit=rebuild_dependents, read_only=True)
                    else:
                        with self._transaction(store):
                            rebuild_dependents(store._projection.graph, self._capture)
                    replaced = store.commit_result_rebuild(staged)
                    self._workspaces.replace_result_ids(replaced)
            except Exception as error:
                print(f"Workbench rebuild failed for {target!r}: {error}", file=sys.stderr)
                raise
            return {"status": "ready", "target": target,
                    "result_ids": {old: item["query_id"] for old, item in replaced.items()}}

