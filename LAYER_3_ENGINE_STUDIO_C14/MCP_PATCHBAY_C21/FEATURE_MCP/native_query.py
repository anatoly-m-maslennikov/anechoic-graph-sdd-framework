"""Serve an explicitly selected native Project's startup snapshot through Workbench."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import threading
from typing import Any

from workbench_tools import CHECK, PAGE, RUN, SCHEMA

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.audit_tables import TABLES as AUDIT_TABLES, create_tables
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_cache import (
    clear_import_sources, read_import_sources, replace_import_sources,
)
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import remove_imports, replace_imports
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import project_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import NativeCapture, capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_log import QueryLog
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.result_delivery import deliver, validate_delivery
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.saved_queries import SavedQueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.service_interface import ServiceInterface
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher import SourceWatcher
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.statements import select_statement
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workspace import WorkspaceStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.watcher_change_log import WatcherChangeLog, mirror_change_log
from native_project_selection import ManifestIdentity, NativeProjectSelection
from work_journal import validated_journal_root


@dataclass(frozen=True)
class NativeQueryInputs:
    """Trusted startup inputs from a compiled model and an optional migration map.

    Omit a legacy reference with None when only the original path identifies a revision.
    """

    validate_manifest: Callable[[dict[str, object], str], ManifestIdentity]
    relation_types: frozenset[str]
    inverses: Mapping[str, str]
    migration_refs: tuple[tuple[str | None, str, str], ...] = ()
    extension_directory: Path | None = None
    require_atom_state: bool = False


def create_native_gateway(root: Path, control_root: str, inputs: NativeQueryInputs):
    from direct_gateway import DirectGateway
    from native_project_selection import resolve_native_project

    selection = resolve_native_project(root, control_root, validate_manifest=inputs.validate_manifest,
                                       require_atom_state=inputs.require_atom_state)
    return DirectGateway(selection.root, native_query=NativeQueryOwner(selection, inputs))


QUERY_TOOLS = frozenset({RUN, PAGE, CHECK, SCHEMA})
LIFECYCLE_TOOLS = frozenset({
    "atom_lifecycle_direct_update", "atom_lifecycle_create_draft", "atom_lifecycle_change_status",
    "atom_lifecycle_archive", "atom_lifecycle_promote_draft", "atom_lifecycle_update",
})
ATOM_TABLES = frozenset({
    "atoms", "relations", "native_references", "native_legacy_references", "native_migration_paths",
})
REALIZATION_TABLES = frozenset({
    "import_nodes", "module_imports", "import_edges", "package_imports", "test_edges", "tested_by_edges",
})
IMPORT_CACHE_TABLES = frozenset(f"_anechoic_import_cache.{name}" for name in ("sources", "sites", "version"))
OBSERVATION_TABLES = frozenset({"change_log", "query_log", "live_runs", "runtime_diagnostics"})
QUERY_TABLES = ATOM_TABLES | REALIZATION_TABLES | OBSERVATION_TABLES | frozenset(AUDIT_TABLES)


class NativeQueryOwner(ServiceInterface):
    def __init__(self, selection: NativeProjectSelection, inputs: NativeQueryInputs) -> None:
        self.selection = selection
        self._root = selection.root
        self._inputs = inputs
        self._store: QueryStore | None = None
        self._capture: NativeCapture | None = None
        paths = selection.parameters.get("paths", {})
        if not isinstance(paths, dict):
            raise ValueError("Project Manifest paths must be a mapping")
        journal_root = paths.get("journal_root", (selection.control_relative / "_journal").as_posix())
        journal_path = validated_journal_root(self._root, journal_root)
        if (journal_path.parts[0].startswith(".anechoic_")
                and journal_path.parts[0] != selection.control_relative.name):
            raise ValueError("Native Journal cannot use another records tree")
        self._saved_queries = SavedQueryStore(self._root, journal_root=journal_path.as_posix())
        self._workspaces = WorkspaceStore(self._root, transient_results=True)
        self._query_log = QueryLog(self._root)
        self._change_log = WatcherChangeLog(self._root)
        self._interface_lock = threading.RLock()
        self._watcher: SourceWatcher | None = None
        self._import_thread: threading.Thread | None = None
        self._import_stop = threading.Event()
        self._realization_options: tuple[tuple[str, ...], tuple[str, ...]] | None = None

    def _import_options(self, workbench: dict) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
        if "import_graph" not in workbench:
            return None
        config = workbench["import_graph"]
        if not isinstance(config, dict):
            raise ValueError("runtime.workbench.import_graph must be a mapping")
        result = []
        for name, default in (("python_roots", ["."]), ("include", [])):
            values = config.get(name, default)
            if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"import_graph.{name} must be a list of Project-relative paths")
            for value in values:
                path = Path(value)
                if path.is_absolute() or ".." in path.parts or not (self._root / path).resolve().is_relative_to(self._root.resolve()):
                    raise ValueError(f"import_graph.{name} paths must be inside the Project")
                if name == "include" and (path == Path(".") or (self._root / path).is_dir()):
                    raise ValueError("import_graph.include paths must name source files")
            result.append(tuple(values))
        return result[0], result[1]

    def _prepare_realization(self, store, *, changes=None, force_parse=False):
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import capture, relevant_change
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution import resolve_realization

        assert self._realization_options is not None
        roots, include = self._realization_options
        with store._lock:
            previous = read_import_sources(store._connection)
        if changes is not None and not relevant_change(self._root, changes, previous):
            return None
        sources = capture(self._root, None if force_parse else previous, include, changes=changes)
        return previous, sources, resolve_realization(self._root, sources, roots)

    @staticmethod
    def _publish_realization(connection, graph, prepared) -> None:
        previous, sources, facts = prepared
        replace_import_sources(connection, sources, previous)
        replace_imports(connection, graph, *facts)

    def _watch_imports(self, store: QueryStore) -> None:

        assert self._watcher is not None
        while not self._import_stop.is_set():
            batch = self._watcher.changes(timeout=0.1)
            try:
                if batch:
                    with self._interface_lock:
                        prepared = self._prepare_realization(store, changes=batch)
                        if prepared is not None:
                            with store._lock, self._transaction(store):
                                self._publish_realization(store._connection, store._projection.graph, prepared)
            except Exception as error:
                print(f"Realization Graph refresh failed. Batch discarded. {error}", file=sys.stderr)

    def _project(self, store: QueryStore, *, use_retained=False, before_commit=None) -> NativeCapture:
        capture = capture_native(self.selection)
        project_native(store, capture, relation_types=self._inputs.relation_types,
                       inverses=self._inputs.inverses, migration_refs=self._inputs.migration_refs,
                       use_retained=use_retained, before_commit=before_commit)
        return capture

    def start(self) -> None:
        runtime = self.selection.parameters.get("runtime", {})
        workbench = runtime.get("workbench", {}) if isinstance(runtime, dict) else None
        if not isinstance(workbench, dict):
            raise ValueError("Project Manifest runtime.workbench must be a mapping")
        self._realization_options = self._import_options(workbench)
        options = {key: workbench[key] for key in ("result_ttl_seconds", "schema_mode") if key in workbench}
        path = self._root / ".anechoic_runtime" / "workbench" / "projection.duckdb"
        spill = path.parent / "duckdb-temp"
        if path.resolve() != path or spill.resolve() != spill:
            raise ValueError("Workbench database and spill paths must use the Project runtime directory directly")
        store = QueryStore(extension_directory=self._inputs.extension_directory,
                           database_path=path, native=True, **options)
        try:
            prepared = None
            if self._realization_options is not None:
                from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import excluded_source_path

                self._watcher = SourceWatcher(
                    self._root, self._root / self.selection.control_relative,
                    implementation_root=self._root, exclude_directory=excluded_source_path,
                )
                self._watcher.start()
                prepared = self._prepare_realization(store)

            def finish(graph) -> None:
                if prepared is None:
                    remove_imports(store._connection, graph)
                    clear_import_sources(store._connection)
                else:
                    self._publish_realization(store._connection, graph, prepared)

            self._capture = self._project(store, use_retained=True, before_commit=finish)
            store.sync_change_log(self._change_log, initialize=True)
            store.record_query_attempts(self._query_log.bind(
                lambda record: store.record_query_attempts([record])
            ))
            self._workspaces.clear_transient_results()
            if self._watcher is not None:
                self._import_thread = threading.Thread(target=self._watch_imports, args=(store,),
                                                       name="native-realization-graph", daemon=True)
                self._import_thread.start()
        except BaseException as error:
            print(f"Native Workbench startup failed: {error}", file=sys.stderr)
            if self._watcher is not None:
                self._watcher.close()
                self._watcher = None
            store.close()
            raise
        self._store = store

    def _refresh_after_write(self, store: QueryStore) -> None:
        try:
            self._capture = self._project(store)
        except Exception:
            self._capture = None
            with store._lock:
                store._available = False
            raise

    @staticmethod
    @contextmanager
    def _transaction(store: QueryStore):
        connection = store._connection
        connection.execute("BEGIN TRANSACTION")
        try:
            yield
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise

    def _rebuild_observations(self, store: QueryStore, target: str, query_attempts) -> None:
        connection = store._connection
        if target in ("all", "change_log"):
            mirror_change_log(connection, self._change_log, initialize=True, in_transaction=True)
        if target in ("all", "query_log"):
            connection.execute("DELETE FROM main.query_log_records")
            store.record_query_attempts(query_attempts)
        if target in ("all", "live_runs"):
            connection.execute("DELETE FROM main.live_runs")
            if store._live_runs:
                connection.executemany("INSERT INTO main.live_runs VALUES (?, ?, ?, ?)", store._live_runs)
        if target in ("all", "runtime_diagnostics"):
            connection.execute("DELETE FROM main.runtime_diagnostics")
            if store._diagnostic_rows:
                connection.executemany(
                    "INSERT INTO main.runtime_diagnostics VALUES (?, ?, ?, ?, ?, ?, ?)",
                    store._diagnostic_rows,
                )
        if target == "all" or target in AUDIT_TABLES:
            create_tables(connection)

    def _rebuild_scope(self, store: QueryStore, target: str) -> tuple[str, str, set[str] | None]:
        if not isinstance(target, str):
            raise ValueError("Workbench rebuild target must be a table name or all")
        table = target.removeprefix("main.")
        if table == "all":
            return table, "all", None
        if table == "workbench_results":
            return table, "results", None
        if re.fullmatch(r"(?:workbench_results\.)?(?:query_)?[a-f0-9]{32}", table):
            return table, "result", None
        atom_tables = ATOM_TABLES | {"scope_units", "internal.reference", "internal.native_exact_refs",
                                     "internal.native_frontier"}
        atom_tables |= {f"internal.{name[1:-1]}" for name in store._projection.graph.tables.values()}
        if table in atom_tables:
            return table, "atoms", atom_tables | set(AUDIT_TABLES) | {"anechoic"}
        if table in REALIZATION_TABLES or table in IMPORT_CACHE_TABLES:
            if self._realization_options is None:
                raise ValueError("Realization Graph is disabled")
            return table, "realization", set(REALIZATION_TABLES | IMPORT_CACHE_TABLES | {"anechoic"})
        if table in ("query_log_records", "query_log"):
            return "query_log", "observation", {"query_log", "query_log_records"}
        if table in OBSERVATION_TABLES or table in AUDIT_TABLES:
            return table, "observation", {table}
        raise ValueError(f"Unknown Workbench rebuild target: {target}")

    def rebuild(self, target: str) -> dict[str, Any]:
        """Rebuild the selected projection and dependent tables on the existing connection."""
        with self._interface_lock:
            store = self._owner()
            table, scope, dependent_inputs = self._rebuild_scope(store, target)
            staged = {}
            try:
                prepared = (self._prepare_realization(store, force_parse=scope == "all" or table in IMPORT_CACHE_TABLES)
                            if scope in ("all", "realization") and self._realization_options is not None else None)

                observations = self._query_log.snapshot() if table in ("all", "query_log") else nullcontext([])
                with observations as query_attempts, store._lock:
                    def rebuild_dependents(graph) -> None:
                        nonlocal staged
                        if prepared is not None:
                            self._publish_realization(store._connection, graph, prepared)
                        elif scope == "all":
                            remove_imports(store._connection, graph)
                            clear_import_sources(store._connection)
                        self._rebuild_observations(store, table, query_attempts)
                        if scope == "atoms":
                            create_tables(store._connection)
                        staged = store.prepare_result_rebuild(table if scope == "result" else None,
                                                              tables=dependent_inputs)

                    store.prune_results()
                    if scope in ("all", "atoms"):
                        self._capture = self._project(store, before_commit=rebuild_dependents)
                    else:
                        with self._transaction(store):
                            rebuild_dependents(store._projection.graph)
                    replaced = store.commit_result_rebuild(staged)
                    self._workspaces.replace_result_ids(replaced)
            except Exception as error:
                print(f"Workbench rebuild failed for {target}: {error}", file=sys.stderr)
                raise
            return {"status": "ready", "target": target,
                    "result_ids": {old: item["query_id"] for old, item in replaced.items()}}

    def lifecycle(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        from ATOM_LIFECYCLE.assets.change_current_status import WORKFLOW_BINDING
        from ATOM_LIFECYCLE.common import InputError, SourceChanged, result
        from ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
        from ATOM_LIFECYCLE.native_update import archive_ticket, change_ticket_status, direct_update
        from native_workflow_definition import NativeWorkflowDefinitionError, bind_status_specifications
        from project_runtime import bind_native_runtime

        if name not in LIFECYCLE_TOOLS:
            raise ValueError("The native Atom Lifecycle Tool is unavailable")
        with self._interface_lock, bind_native_runtime(self.selection):
            store = self._owner()
            assert self._capture is not None
            try:
                from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import read_structure

                snapshot_path = getattr(self.selection, "structure_snapshot", None)
                try:
                    structure_snapshot = read_structure(snapshot_path) if snapshot_path is not None else None
                except (OSError, RuntimeError, TypeError, ValueError) as error:
                    raise SourceChanged("Structure snapshot is unavailable or invalid.") from error
                rows = self._capture.atoms
                if name in {"atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft"}:
                    field = "target" if name == "atom_lifecycle_promote_draft" else "sourceCurrent"
                    target = arguments.get(field)
                    ref = target.get("ref_id") if isinstance(target, dict) else None
                    if isinstance(ref, str) and any(
                        old in WORKFLOW_BINDING.values() and native.partition("@")[0] == ref.partition("@")[0]
                        for old, _, native in self._inputs.migration_refs
                    ):
                        raise InputError(field, "Installed status definitions can change only with their runtime binding.")
                if name == "atom_lifecycle_direct_update":
                    outcome = direct_update(self.selection, arguments, current_rows=rows)
                elif name in {"atom_lifecycle_create_draft", "atom_lifecycle_update"}:
                    outcome = create_draft(self.selection, arguments, current_rows=rows, structure_snapshot=structure_snapshot)
                elif name == "atom_lifecycle_archive":
                    outcome = archive_ticket(self.selection, arguments, current_rows=rows)
                elif name == "atom_lifecycle_promote_draft":
                    outcome = promote_draft(
                        self.selection, arguments, current_rows=rows, migration_refs=self._inputs.migration_refs,
                        structure_snapshot=structure_snapshot,
                    )
                else:
                    check_definition = bind_status_specifications(
                        self.selection, current_rows=rows, migration_refs=self._inputs.migration_refs,
                    )
                    outcome = change_ticket_status(
                        self.selection, arguments, current_rows=rows, check_definition=check_definition,
                    )
            except InputError as error:
                return result(outcome="needs_input", requested_input=error.requested_input)
            except SourceChanged as error:
                return result(errors=[{"code": "source_changed", "message": str(error)}])
            except NativeWorkflowDefinitionError as error:
                return result(outcome="blocked", errors=[{
                    "code": "definition_revalidation_required", "message": str(error),
                }])
            if outcome.get("effects"):
                try:
                    self._refresh_after_write(store)
                except Exception:
                    outcome["outcome"] = "failed"
                    outcome.setdefault("errors", []).append({
                        "code": "projection_refresh_failed",
                        "message": "Workbench could not refresh after the Atom Lifecycle effect. Restart required.",
                    })
            return outcome

    def _start(self) -> None:
        self._owner()

    def _flush_lifecycle_changes(self) -> None:
        self._owner()

    def save_view(self, sql: str, name: str | None = None) -> dict[str, Any]:
        return self._saved_queries.save_view(sql, name)

    def load(self, reference: str) -> dict[str, Any]:
        return self._saved_queries.load(reference)

    def saved_list(self, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        return self._saved_queries.list(limit)

    def _owner(self) -> QueryStore:
        if self._store is None or self._capture is None:
            raise RuntimeError("Native query projection is unavailable")
        return self._store

    def status(self) -> dict[str, str]:
        self._owner()
        return {"mode": "startup_snapshot"}

    def page(self, query_id: str, offset: int, page_size: int = 100, *, grid: object = None,
             preview: int | None = None, result_delivery: str = "file",
             result_format: str = "json_matrix") -> dict[str, Any]:
        validate_delivery(result_delivery, result_format)
        store = self._owner()
        store.prune_results()
        result = store.page(query_id, offset, page_size=page_size, grid=grid, preview=preview)
        return deliver(store, self.selection.root, result, result_delivery, result_format)

    def check(self, sql: str, cursor_position: int | None = None) -> dict[str, Any]:
        result = self._owner().check(select_statement(sql, cursor_position))
        result.pop("sql", None)
        return result

    def schema(self) -> dict[str, Any]:
        tables = self._owner().schema()["tables"]
        return {"tables": {name: columns for name, columns in tables.items() if name in QUERY_TABLES}}

    def close(self) -> None:
        self._import_stop.set()
        if self._import_thread is not None:
            self._import_thread.join()
            self._import_thread = None
        if self._watcher is not None:
            self._watcher.close()
            self._watcher = None
        self._query_log.close()
        self._capture = None
        if self._store is not None:
            self._store.close()
            self._store = None
