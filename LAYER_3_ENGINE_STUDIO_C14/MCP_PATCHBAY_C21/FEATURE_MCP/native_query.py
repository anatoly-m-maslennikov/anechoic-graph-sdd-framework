"""Serve an explicitly selected native Project through Workbench."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import sys
import threading
from typing import Any

from workbench_tools import CHECK, PAGE, RUN, SCHEMA

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.component_metrics import realization_component_paths
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.audit_tables import TABLES as AUDIT_TABLES, create_tables
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.errors import WorkbenchUnavailableError
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_cache import (
    clear_import_sources, read_import_sources, replace_import_sources,
)
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import remove_imports, replace_imports
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import (
    project_native, project_native_delta, replace_component_metrics,
)
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import (
    NativeCapture, NativeManifestChanged, capture_native,
)
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.package_audit import replace_package_audit
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_admission import is_duckdb_internal
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_log import QueryLog
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.result_delivery import deliver, validate_delivery
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.saved_queries import SavedQueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.service_interface import ServiceInterface
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher import SourceWatcher
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.spec_trace import (
    PACKAGE_SUFFIX, SUFFIX, is_trace_path, native_trace_snapshot, remove_native_traces, replace_native_traces,
)
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.statements import select_statement
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workspace import WorkspaceStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.watcher_change_log import WatcherChangeLog, mirror_change_log
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.structure_host_pkg3.snapshot import read_structure
from native_project_selection import ManifestIdentity, NativeProjectSelection, resolve_native_project
from work_journal import PROJECT_DATABASE, journal_storage, pending_database_journal, validated_journal_root


@dataclass(frozen=True)
class NativeQueryInputs:
    """Trusted startup inputs from the compiled native Model."""

    validate_manifest: Callable[[dict[str, object], str], ManifestIdentity]
    relation_types: frozenset[str]
    inverses: Mapping[str, str]
    extension_directory: Path | None = None
    require_atom_state: bool = False
    require_atom_header: bool = False
    ticket_labels: tuple[str, ...] = ()


def create_native_gateway(root: Path, control_root: str, inputs: NativeQueryInputs):
    from direct_gateway import DirectGateway

    selection = resolve_native_project(root, control_root, validate_manifest=inputs.validate_manifest,
                                       require_atom_state=inputs.require_atom_state,
                                       require_atom_header=inputs.require_atom_header)
    return DirectGateway(selection.root, native_query=NativeQueryOwner(selection, inputs))


QUERY_TOOLS = frozenset({RUN, PAGE, CHECK, SCHEMA})
LIFECYCLE_TOOLS = frozenset({
    "atom_lifecycle_direct_update", "atom_lifecycle_create_draft", "atom_lifecycle_change_status",
    "atom_lifecycle_archive", "atom_lifecycle_promote_draft", "atom_lifecycle_update",
})
ATOM_TABLES = frozenset({
    "atoms", "relations", "native_references", "components",
})
REALIZATION_TABLES = frozenset({
    "import_nodes", "module_imports", "import_edges", "package_imports", "test_edges", "tested_by_edges",
    "import_read_issues", "implementation_rmedo", "component_metrics", "package_audit",
})
IMPORT_CACHE_TABLES = frozenset(f"_anechoic_import_cache.{name}" for name in ("sources", "sites", "version"))
OBSERVATION_TABLES = frozenset({"change_log", "query_log", "live_runs", "runtime_diagnostics"})
QUERY_TABLES = ATOM_TABLES | REALIZATION_TABLES | OBSERVATION_TABLES | frozenset(AUDIT_TABLES) | {"work_journal"}


def _test_asset_change(root: Path, relative: str) -> bool:
    parts = (root.name, *PurePosixPath(relative).parts)
    return any(test == parent + "__tests" and child == "assets"
               for parent, test, child in zip(parts, parts[1:], parts[2:]))


class NativeQueryOwner(ServiceInterface):
    def __init__(self, selection: NativeProjectSelection, inputs: NativeQueryInputs) -> None:
        self.selection = selection
        self._projection_selection = selection
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
        self._journal_mode = journal_storage(selection.parameters)
        self._saved_queries = SavedQueryStore(
            self._root, journal_root=journal_path.as_posix(), journal_mode=self._journal_mode,
            read_journal_events=self._saved_journal_events,
        )
        self._workspaces = WorkspaceStore(self._root, transient_results=True)
        self._query_log = QueryLog(self._root)
        self._change_log = WatcherChangeLog(self._root)
        self._interface_lock = threading.RLock()
        self._watcher: SourceWatcher | None = None
        self._watch_thread: threading.Thread | None = None
        self._watch_stop = threading.Event()
        self._realization_options: tuple[tuple[str, ...], tuple[str, ...]] | None = None

    def _import_options(self, workbench: dict) -> tuple[tuple[str, ...], tuple[str, ...]] | None:
        config = workbench.get("import_graph", {})
        if config is False:
            return None
        if not isinstance(config, dict):
            raise ValueError("runtime.workbench.import_graph must be a mapping or false")
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
        if changes is not None:
            measurements_changed = any(
                is_trace_path(path) or _test_asset_change(self._root, path)
                for change in changes for key in ("old_path", "new_path") if (path := change.get(key)) is not None
            )
            if not measurements_changed and not relevant_change(self._root, changes, previous):
                return None
        sources = capture(self._root, None if force_parse else previous, include, changes=changes)
        component_paths = {".": "C00"}
        if self.selection.structure_snapshot is not None:
            snapshot = read_structure(self.selection.structure_snapshot)
            folders = {PurePosixPath(path).parent for path in sources}
            component_paths = realization_component_paths(self.selection, snapshot, folders)
        facts = resolve_realization(self._root, sources, roots, components=component_paths)
        return previous, sources, facts, native_trace_snapshot(self._root, facts[0])

    @staticmethod
    def _publish_realization(store, graph, prepared) -> dict[str, str]:
        connection = store._connection
        previous, sources, facts, (traces, binding_states) = prepared
        nodes, occurrences, edges, tests, test_keys = facts
        replace_import_sources(connection, sources, previous)
        replace_imports(connection, graph, nodes, occurrences, edges, tests, sources=sources, test_keys=test_keys,
                        mark_graph_changed=store.mark_graph_registration_changed)
        replace_native_traces(connection, traces)
        return binding_states

    def _publish_realization_metadata(self, store: QueryStore, capture: NativeCapture,
                                      binding_states: dict[str, str] | None = None, *, atoms_only=False) -> None:
        from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.component_metrics import measure_components, refresh_spec_sizes

        connection = store._connection
        if self._realization_options is None:
            connection.execute("DROP TABLE IF EXISTS main.component_metrics")
            connection.execute("DROP TABLE IF EXISTS main.package_audit")
            return
        nodes = connection.execute(
            "SELECT node_key, kind, language, relative_path, scan_status, package_key, package_type FROM main.import_nodes"
        ).fetchall()
        tests = connection.execute("SELECT source_key, target_key FROM main.test_edges").fetchall()
        replace_package_audit(connection, self.selection, capture, nodes,
                              binding_states, tests=tests)
        if atoms_only:
            measurements = refresh_spec_sizes(connection, capture, self.selection.project_prefix)
        else:
            sources = read_import_sources(connection)
            try:
                measurements = measure_components(self.selection, capture, sources, nodes, tests)
            except (OSError, RuntimeError, ValueError) as error:
                print(f"Component metrics unavailable: {error}", file=sys.stderr)
                measurements = []
        replace_component_metrics(connection, measurements)

    def _refresh_traces(self, store: QueryStore, paths: set[str]) -> None:
        owners = set()
        for relative in paths:
            path = PurePosixPath(relative)
            parent_name = path.parent.name or self._root.name
            if path.name == parent_name + PACKAGE_SUFFIX or path.name == parent_name + '.p' + SUFFIX:
                owners.add(('package', path.parent.as_posix()))
            elif path.name.endswith(SUFFIX) and path.name != SUFFIX:
                owners.add(('module', path.with_name(path.name.removesuffix(SUFFIX)).as_posix()))
        connection = store._connection
        with store._lock, self._transaction(store):
            nodes = []
            for kind, relative in owners:
                nodes.extend(connection.execute(
                    'SELECT node_key, kind, language, relative_path, scan_status, package_key '
                    'FROM main.import_nodes WHERE kind = ? AND relative_path = ?', [kind, relative],
                ).fetchall())
            traces, states = native_trace_snapshot(self._root, nodes)
            for _, kind, _, relative, _, _ in nodes:
                connection.execute('DELETE FROM main.implementation_rmedo WHERE owner_path = ?', [relative])
                if kind == 'package':
                    states.setdefault(relative, 'missing')
            if traces:
                connection.executemany('INSERT INTO main.implementation_rmedo VALUES (?, ?, ?, ?, ?)', traces)
            if states:
                retained = dict(connection.execute(
                    'SELECT relative_path, binding_status FROM main.package_audit').fetchall())
                retained.update(states)
                nodes = connection.execute(
                    'SELECT node_key, kind, language, relative_path, scan_status, package_key, package_type '
                    'FROM main.import_nodes').fetchall()
                tests = connection.execute('SELECT source_key, target_key FROM main.test_edges').fetchall()
                replace_package_audit(connection, self.selection, self._capture, nodes,
                                      retained, tests=tests)

    def _watch_sources(self, store: QueryStore) -> None:
        assert self._watcher is not None
        pending: set[PurePosixPath] | None = set()
        while not self._watch_stop.is_set() and store._available:
            batch = self._watcher.changes(timeout=0.1)
            if self._journal_mode == "duckdb":
                try:
                    store.sync_work_journal(self._root)
                except Exception as error:
                    print(f"Native Work Journal refresh failed: {error}", file=sys.stderr)
            if not batch:
                continue
            with self._interface_lock:
                if self._watch_stop.is_set() or not store._available:
                    break
                pending = self._watch_atom_changes(store, batch, pending)
                if self._realization_options is not None and store._available:
                    try:
                        paths = {path for change in batch for key in ('old_path', 'new_path')
                                 if (path := change.get(key)) is not None}
                        if (paths and all(is_trace_path(path) and not _test_asset_change(self._root, path)
                                          and not PurePosixPath(path).is_relative_to(self.selection.control_relative)
                                          for path in paths)):
                            self._refresh_traces(store, paths)
                            continue
                        prepared = self._prepare_realization(store, changes=batch)
                        if prepared is not None:
                            with store._lock, self._transaction(store):
                                bindings = self._publish_realization(store, store._projection.graph, prepared)
                                self._publish_realization_metadata(store, self._capture, bindings)
                    except Exception as error:
                        print(f"Realization Graph refresh failed. Batch discarded. {error}", file=sys.stderr)

    def _watch_atom_changes(self, store: QueryStore, batch, pending):
        changed = self._atom_source_paths(batch)
        if changed is not None and not changed:
            return pending
        pending = None if changed is None or pending is None else pending | changed
        try:
            self._capture = self._refresh_atom_sources(store, pending)
        except Exception as error:
            print(f"Native Atom refresh failed: {error}", file=sys.stderr)
            return pending
        return set()

    def _atom_source_paths(self, batch) -> set[PurePosixPath] | None:
        control = self.selection.control_relative
        generated = control / "000_ANECHOIC_framework"
        files: set[PurePosixPath] = set()
        for change in batch:
            for key in ("old_path", "new_path"):
                raw_path = change.get(key)
                if raw_path is None:
                    continue
                path = PurePosixPath(raw_path)
                if not path.is_relative_to(control) or path.is_relative_to(generated):
                    continue
                if path.suffix == ".md" or (self._root / path).is_dir() or (key == "old_path" and any(
                    raw_path != row["source_path"] and row["source_path"].startswith(raw_path + "/")
                    for row in self._capture.atoms
                )):
                    files.add(path)
        return files

    def _capture_for_projection(self, paths=None) -> tuple[NativeCapture, NativeProjectSelection]:
        selection = self._projection_selection
        try:
            return capture_native(selection, previous=self._capture, paths=paths), selection
        except NativeManifestChanged:
            selection = resolve_native_project(
                self._root, self.selection.control_relative, validate_manifest=self._inputs.validate_manifest,
                require_atom_state=self._inputs.require_atom_state, require_atom_header=self._inputs.require_atom_header,
            )
            if (selection.project_name != self.selection.project_name
                    or selection.project_prefix != self.selection.project_prefix
                    or selection.manifest_ref.partition("@")[0] != self.selection.manifest_ref.partition("@")[0]):
                raise ValueError("Project identity changed. Restart required.")
            return capture_native(selection), selection

    def _refresh_atom_sources(self, store: QueryStore, paths: set[PurePosixPath] | None) -> NativeCapture:
        previous = self._capture
        capture, selection = self._capture_for_projection(paths)
        if capture != previous:
            before = {row["source_path"]: row["_source_sha256"] for row in previous.atoms}
            after = {row["source_path"]: row["_source_sha256"] for row in capture.atoms}
            paths = {PurePosixPath(path) for path in before.keys() | after.keys()
                     if before.get(path) != after.get(path)}
            if not project_native_delta(
                store, capture, paths=paths, relation_types=self._inputs.relation_types,
                inverses=self._inputs.inverses,
                component_ids=self._component_ids(),
                before_commit=lambda graph: self._publish_realization_metadata(store, capture, atoms_only=True),
            ):
                self._project(store, capture=capture)
        self._projection_selection = selection
        return capture

    def _component_ids(self) -> list[str]:
        component_ids = ["C00"]
        if self._realization_options is not None and self.selection.structure_snapshot is not None:
            component_ids.extend(read_structure(self.selection.structure_snapshot).components)
        return component_ids

    def _project(self, store: QueryStore, *, use_retained=False, before_commit=None,
                 capture: NativeCapture | None = None, read_only=False) -> NativeCapture:
        selection = self.selection
        if capture is None:
            if read_only:
                capture, selection = self._capture_for_projection()
            else:
                capture = capture_native(self.selection)

        def finish(graph) -> None:
            if before_commit is None:
                self._publish_realization_metadata(store, capture)
            else:
                before_commit(graph, capture)

        project_native(store, capture, relation_types=self._inputs.relation_types, component_ids=self._component_ids(),
                       inverses=self._inputs.inverses,
                       use_retained=use_retained, before_commit=finish)
        self._projection_selection = selection
        return capture

    def _open_store(self, workbench: dict) -> QueryStore:
        from duckdb import IOException

        storage = workbench.get("storage", "disk")
        if storage not in ("disk", "memory"):
            raise ValueError("Project Manifest runtime.workbench.storage must be disk or memory")
        options = {key: workbench[key] for key in ("result_ttl_seconds", "schema_mode", "inline_result_limit_kib")
                   if key in workbench}
        path = self._root / PROJECT_DATABASE
        spill = path.parent / "duckdb-temp"
        if path.resolve() != path or spill.resolve() != spill:
            raise ValueError("Workbench database and spill paths must use the Project runtime directory directly")
        try:
            journal_disk = self._journal_mode == "duckdb" or pending_database_journal(self._root)
            return QueryStore(
                extension_directory=self._inputs.extension_directory,
                database_path=path if storage == "disk" else None,
                journal_path=path if journal_disk or (storage == "memory" and path.is_file()) else None,
                journal_disk=journal_disk, native=True, **options,
            )
        except IOException as error:
            if "Could not set lock on file" in str(error):
                raise WorkbenchUnavailableError(
                    "This Project is already open. Connect to its HTTP server if available."
                ) from error
            raise

    def start(self) -> None:
        store = None
        try:
            runtime = self.selection.parameters.get("runtime", {})
            workbench = runtime.get("workbench", {}) if isinstance(runtime, dict) else None
            if not isinstance(workbench, dict):
                raise ValueError("Project Manifest runtime.workbench must be a mapping")
            self._realization_options = self._import_options(workbench)
            store = self._open_store(workbench)
            store.sync_work_journal(self._root)
            poll_bind_mount = os.environ.get("ANECHOIC_RUNTIME_NAMESPACE") == "docker"
            prepared = None
            if self._realization_options is not None:
                from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import excluded_source_path

                self._watcher = SourceWatcher(
                    self._root, self.selection.control_root, implementation_root=self._root,
                    exclude_directory=lambda path: (
                        not PurePosixPath(path).is_relative_to(self.selection.control_relative)
                        and excluded_source_path(path, directory=True)
                    ),
                    poll_bind_mount=poll_bind_mount,
                )
            else:
                self._watcher = SourceWatcher(self._root, self.selection.control_root, poll_bind_mount=poll_bind_mount)
            self._watcher.start()
            if self._realization_options is not None:
                prepared = self._prepare_realization(store)

            def finish(graph, capture) -> None:
                bindings = None
                if prepared is None:
                    remove_imports(store._connection, graph, mark_graph_changed=store.mark_graph_registration_changed)
                    clear_import_sources(store._connection)
                    remove_native_traces(store._connection)
                else:
                    bindings = self._publish_realization(store, graph, prepared)
                self._publish_realization_metadata(store, capture, bindings)

            self._capture = self._project(store, use_retained=True, before_commit=finish)
            store.sync_change_log(self._change_log, initialize=True)
            store.record_query_attempts(self._query_log.bind(
                lambda record: store.record_query_attempts([record])
            ))
            self._workspaces.clear_transient_results()
            self._watch_thread = threading.Thread(target=self._watch_sources, args=(store,),
                                                  name="native-source-watcher", daemon=True)
            self._watch_thread.start()
        except BaseException as error:
            print(f"Native Workbench startup failed: {error}", file=sys.stderr)
            if self._watcher is not None:
                self._watcher.close()
                self._watcher = None
            if store is not None:
                store.close()
            raise
        self._store = store

    def _lifecycle_atom_paths(self, effects) -> set[PurePosixPath] | None:
        changes = []
        for effect in effects:
            if not isinstance(effect, dict):
                return None
            operation, target = effect.get("operation"), effect.get("target")
            if (operation not in ("create", "modify", "remove") or effect.get("state") != "known"
                    or not isinstance(target, str) or not target):
                return None
            path = PurePosixPath(target)
            if path.is_absolute() or ".." in path.parts:
                return None
            if effect.get("evidence") in ("directory", "directory created", "directory absent after removal"):
                continue
            key = "old_path" if operation == "remove" else "new_path"
            changes.append({key: target})
        return self._atom_source_paths(changes)

    def _refresh_after_write(self, store: QueryStore, effects=None) -> None:
        try:
            paths = self._lifecycle_atom_paths(effects) if effects is not None else None
            if paths is None:
                self._capture = self._project(store)
            elif paths:
                self._capture = self._refresh_atom_sources(store, paths)
        except Exception:
            self._capture = None
            with store._lock:
                store._available = False
            raise

    @staticmethod
    @contextmanager
    def _transaction(store: QueryStore):
        connection = store._connection
        if not store._available:
            raise WorkbenchUnavailableError("Workbench unavailable; restart required")
        store._graph_registration_changed = False
        connection.execute("BEGIN TRANSACTION")
        try:
            yield
            connection.execute("COMMIT")
        except BaseException as error:
            if store._graph_registration_changed or is_duckdb_internal(error):
                store._available = False
            try:
                connection.execute("ROLLBACK")
            except Exception:
                store._available = False
                raise
            if not store._available:
                raise WorkbenchUnavailableError("Workbench unavailable; restart required") from error
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
            return table, "atoms", atom_tables | set(AUDIT_TABLES) | {"anechoic", "component_metrics", "package_audit"}
        if table in REALIZATION_TABLES or table in IMPORT_CACHE_TABLES:
            if self._realization_options is None:
                raise ValueError("Realization Graph is disabled")
            return table, "realization", set(REALIZATION_TABLES | IMPORT_CACHE_TABLES | {"anechoic"})
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
                            bindings = self._publish_realization(store, graph, prepared)
                        elif scope == "all":
                            remove_imports(store._connection, graph,
                                           mark_graph_changed=store.mark_graph_registration_changed)
                            clear_import_sources(store._connection)
                            remove_native_traces(store._connection)
                        self._rebuild_observations(store, table, query_attempts)
                        if scope == "atoms":
                            create_tables(store._connection)
                        if scope in ("all", "atoms", "realization"):
                            self._publish_realization_metadata(store, capture, bindings)
                        staged = store.prepare_result_rebuild(table if scope == "result" else None,
                                                              tables=dependent_inputs)

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

    def lifecycle(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        from ATOM_LIFECYCLE.common import InputError, SourceChanged, result
        from ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
        from ATOM_LIFECYCLE.native_update import archive_ticket, change_ticket_status, direct_update
        from native_workflow_definition import (
            STATUS_SPECIFICATIONS, NativeWorkflowDefinitionError, bind_status_specifications,
        )
        from project_runtime import bind_native_runtime

        if name not in LIFECYCLE_TOOLS:
            raise ValueError("The native Atom Lifecycle Tool is unavailable")
        with self._interface_lock, bind_native_runtime(self.selection):
            store = self._owner()
            assert self._capture is not None
            try:

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
                        native.partition("@")[0] == ref.partition("@")[0]
                        for native, _ in STATUS_SPECIFICATIONS.values()
                    ):
                        raise InputError(field, "Installed status definitions can change only with their runtime binding.")
                if name == "atom_lifecycle_direct_update":
                    outcome = direct_update(self.selection, arguments, current_rows=rows)
                elif name in {"atom_lifecycle_create_draft", "atom_lifecycle_update"}:
                    outcome = create_draft(self.selection, arguments, current_rows=rows,
                                           structure_snapshot=structure_snapshot, ticket_labels=self._inputs.ticket_labels)
                elif name == "atom_lifecycle_archive":
                    outcome = archive_ticket(self.selection, arguments, current_rows=rows)
                elif name == "atom_lifecycle_promote_draft":
                    outcome = promote_draft(
                        self.selection, arguments, current_rows=rows,
                        structure_snapshot=structure_snapshot,
                    )
                else:
                    check_definition = bind_status_specifications(
                        self.selection, current_rows=rows,
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
                    self._refresh_after_write(store, outcome["effects"])
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
        self._owner().sync_work_journal(self._root)

    def _saved_journal_events(self, author: str) -> list[object]:
        if self._store is None and self._journal_mode == "files":
            return []
        store = self._owner()
        store.sync_work_journal(self._root)
        return store.work_journal_events(author)

    def save_view(self, sql: str, name: str | None = None) -> dict[str, Any]:
        return self._saved_queries.save_view(sql, name)

    def load(self, reference: str) -> dict[str, Any]:
        return self._saved_queries.load(reference)

    def saved_list(self, limit: int = 20) -> dict[str, list[dict[str, Any]]]:
        return self._saved_queries.list(limit)

    def _owner(self) -> QueryStore:
        if self._store is None or self._capture is None:
            raise RuntimeError("Native query projection is unavailable")
        if not self._store._available:
            raise WorkbenchUnavailableError("Workbench unavailable; restart required")
        return self._store

    def status(self) -> dict[str, str]:
        self._owner()
        return {"mode": "live_index"}

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
        self._watch_stop.set()
        if self._watch_thread is not None:
            self._watch_thread.join()
            self._watch_thread = None
        if self._watcher is not None:
            self._watcher.close()
            self._watcher = None
        self._query_log.close()
        self._capture = None
        if self._store is not None:
            self._store.close()
            self._store = None
