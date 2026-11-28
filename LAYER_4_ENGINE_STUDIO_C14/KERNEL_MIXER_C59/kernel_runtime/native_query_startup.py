"""Open and publish the native query runtime before serving requests."""

from __future__ import annotations

import os
import sys
import threading
from pathlib import PurePosixPath

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    sources.watch.watch__shared import (
        SourceWatcher,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    settings.project.project__shared import (
        migrate_project_database,
    )  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    settings.journal.journal__shared import (
        pending_database_journal,
    )  # fmt: skip

from .. import realization_projection
from ..component_projection import _write_component_seeds
from ..errors import WorkbenchUnavailableError
from ..import_cache import clear_import_sources
from ..import_tables import remove_imports
from ..query_store import QueryStore
from ..spec_trace import remove_native_traces

_STORE_OPTIONS = (
    "result_ttl_seconds",
    "schema_mode",
    "inline_result_limit_kib",
)


class NativeQueryStartup:
    def _open_store(self, workbench: dict) -> QueryStore:
        from duckdb import IOException

        storage = workbench.get("storage", "disk")
        if storage not in ("disk", "memory"):
            raise ValueError(
                "Project Manifest runtime.iwe_console.storage "
                "must be disk or memory"
            )
        options = {
            key: workbench[key] for key in _STORE_OPTIONS if key in workbench
        }
        path = migrate_project_database(self._root)
        spill = path.parent / "duckdb-temp"
        if path.resolve() != path or spill.resolve() != spill:
            raise ValueError(
                "Workbench database and spill paths must use the "
                "Project runtime directory directly"
            )
        try:
            journal_disk = (
                self._journal_mode == "duckdb"
                or pending_database_journal(self._root)
            )
            return QueryStore(
                extension_directory=self._inputs.extension_directory,
                database_path=path if storage == "disk" else None,
                journal_path=path
                if journal_disk or (storage == "memory" and path.is_file())
                else None,
                journal_disk=journal_disk,
                native=True,
                **options,
            )
        except IOException as error:
            if "Could not set lock on file" in str(error):
                raise WorkbenchUnavailableError(
                    "This Project is already open. "
                    "Connect to its HTTP server if available."
                ) from error
            raise

    def _start_watcher(self) -> None:
        poll_bind_mount = (
            sys.platform == "darwin"
            or os.environ.get("ANECHOIC_RUNTIME_NAMESPACE") == "docker"
        )
        snapshot = self.selection.structure_snapshot
        if self._realization_options is not None or snapshot is not None:
            control = self.selection.control_relative
            self._watcher = SourceWatcher(
                self._root,
                self.selection.control_root,
                implementation_root=self._root,
                watch_root_files=True,
                exclude_directory=lambda path: (
                    realization_projection.exclude_directory(path, control)
                    if self._realization_options is not None
                    else not PurePosixPath(path).is_relative_to(control)
                ),
                additional_directory=snapshot.parent
                if snapshot is not None
                else None,
                poll_bind_mount=poll_bind_mount,
            )
        else:
            self._watcher = SourceWatcher(
                self._root,
                self.selection.control_root,
                watch_root_files=True,
                poll_bind_mount=poll_bind_mount,
            )
        self._watcher.start()

    def start(self) -> None:
        store = None
        try:
            runtime = self.selection.parameters.get("runtime", {})
            workbench = (
                runtime.get("iwe_console", runtime.get("workbench", {}))
                if isinstance(runtime, dict)
                else None
            )
            if not isinstance(workbench, dict):
                raise ValueError(
                    "Project Manifest runtime.iwe_console must be a mapping"
                )
            self._realization_options = self._import_options(workbench)
            store = self._open_store(workbench)
            store.sync_work_journal(self._root)
            self._start_watcher()
            self._capture = self._startup_projection(store)
            self._start_change_tracking(store)
        except BaseException as error:
            print(f"Native Workbench startup failed: {error}", file=sys.stderr)
            if self._watcher is not None:
                self._watcher.close()
                self._watcher = None
            if store is not None:
                store.close()
            raise
        self._store = store

    def _startup_projection(self, store):
        prepared = None
        if self._realization_options is not None:
            prepared = self._prepare_realization(store)

        def finish(graph, capture) -> None:
            bindings = None
            if prepared is None:
                remove_imports(
                    store._connection,
                    graph,
                    mark_graph_changed=store.mark_graph_registration_changed,
                )
                clear_import_sources(store._connection)
                remove_native_traces(store._connection)
            else:
                bindings = realization_projection.publish(
                    store, graph, prepared
                )
            self._publish_realization_metadata(store, capture, bindings)

        return self._project(store, use_retained=True, before_commit=finish)

    def _start_change_tracking(self, store):
        store.sync_change_log(self._change_log, initialize=True)
        store.record_query_attempts(
            self._query_log.bind(
                lambda record: store.record_query_attempts([record])
            )
        )
        self._workspaces.clear_transient_results()
        self._watch_thread = threading.Thread(
            target=self._watch_sources,
            args=(store,),
            name="native-source-watcher",
            daemon=True,
        )
        self._watch_thread.start()

    def _watch_sources(self, store: QueryStore) -> None:
        assert self._watcher is not None
        pending: set[PurePosixPath] | None = set()
        while not self._watch_stop.is_set() and store._available:
            batch = self._watcher.changes(timeout=0.1)
            if self._journal_mode == "duckdb":
                try:
                    store.sync_work_journal(self._root)
                except Exception as error:
                    print(
                        f"Native Work Journal refresh failed: {error}",
                        file=sys.stderr,
                    )
            if not batch:
                continue
            with self._interface_lock:
                if self._watch_stop.is_set() or not store._available:
                    break
                pending = self._watch_atom_changes(store, batch, pending)
                if not store._available:
                    break
                if self._realization_options is None:
                    self._watch_structure_snapshot(store, batch)
                else:
                    self._watch_realization_changes(store, batch)

    def _watch_structure_snapshot(self, store: QueryStore, batch) -> None:
        snapshot = self.selection.structure_snapshot
        if snapshot is None:
            return
        relative = snapshot.relative_to(self._root).as_posix()
        if any(
            relative in (change.get("old_path"), change.get("new_path"))
            for change in batch
        ):
            try:
                with store._lock, self._transaction(store):
                    _write_component_seeds(store._connection, self.selection)
            except Exception as error:
                print(f"Structure refresh failed: {error}", file=sys.stderr)
