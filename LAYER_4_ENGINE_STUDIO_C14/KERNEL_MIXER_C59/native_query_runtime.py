"""Native Workbench query, projection, and persistence owner."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from contextlib import contextmanager
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import sys
import threading
from typing import Any

from . import realization_projection
from .errors import WorkbenchUnavailableError
from .import_cache import clear_import_sources
from .import_tables import remove_imports
from .native_query_projection import NativeQueryProjection
from .native_query_rebuild import NativeQueryRebuild, QUERY_TABLES
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import NativeCapture
from .query_admission import is_duckdb_internal
from .query_log import QueryLog
from .query_store import QueryStore
from .result_delivery import deliver, validate_delivery
from .saved_queries import SavedQueryStore
from .service_interface import ServiceInterface
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import SourceWatcher
from .spec_trace import remove_native_traces
from .statements import select_statement
from .workspace import WorkspaceStore
from .watcher_change_log import WatcherChangeLog
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import ManifestIdentity, NativeProjectSelection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import journal_storage, validated_journal_root
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import pending_database_journal
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import migrate_project_database


@dataclass(config=ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True), frozen=True)
class NativeQueryInputs:
    """Trusted startup inputs from the compiled native Model."""

    validate_manifest: Callable[[dict[str, object], str], ManifestIdentity]
    relation_types: frozenset[str]
    inverses: Mapping[str, str]
    extension_directory: Path | None = None
    require_atom_state: bool = False
    require_atom_header: bool = False
    ticket_labels: tuple[str, ...] = ()
    validate_project_spec: Callable[[str, dict[str, object], str], object] | None = None






class NativeQueryRuntime(NativeQueryProjection, NativeQueryRebuild, ServiceInterface):
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
        if (journal_path.parts[0].startswith((".anechoic_", "_anechoic_"))
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
        self._realization_options: tuple[tuple[str, ...] | None, tuple[str, ...], dict[str, tuple[str, ...]]] | None = None

    def _open_store(self, workbench: dict) -> QueryStore:
        from duckdb import IOException

        storage = workbench.get("storage", "disk")
        if storage not in ("disk", "memory"):
            raise ValueError("Project Manifest runtime.workbench.storage must be disk or memory")
        options = {key: workbench[key] for key in ("result_ttl_seconds", "schema_mode", "inline_result_limit_kib")
                   if key in workbench}
        path = migrate_project_database(self._root)
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

    def _start_watcher(self) -> None:
        poll_bind_mount = os.environ.get("ANECHOIC_RUNTIME_NAMESPACE") == "docker"
        if self._realization_options is not None:
            snapshot = self.selection.structure_snapshot
            self._watcher = SourceWatcher(
                self._root, self.selection.control_root, implementation_root=self._root, watch_root_files=True,
                exclude_directory=lambda path: realization_projection.exclude_directory(
                    path, self.selection.control_relative,
                ),
                additional_directory=snapshot.parent if snapshot is not None else None,
                poll_bind_mount=poll_bind_mount,
            )
        else:
            self._watcher = SourceWatcher(self._root, self.selection.control_root, watch_root_files=True, poll_bind_mount=poll_bind_mount)
        self._watcher.start()

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
            self._start_watcher()
            prepared = None
            if self._realization_options is not None:
                prepared = self._prepare_realization(store)

            def finish(graph, capture) -> None:
                bindings = None
                if prepared is None:
                    remove_imports(store._connection, graph, mark_graph_changed=store.mark_graph_registration_changed)
                    clear_import_sources(store._connection)
                    remove_native_traces(store._connection)
                else:
                    bindings = realization_projection.publish(store, graph, prepared)
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
