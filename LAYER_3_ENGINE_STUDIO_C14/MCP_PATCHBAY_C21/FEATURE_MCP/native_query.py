"""Serve an explicitly selected native Project's startup snapshot through Workbench."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
import sys
import threading
from typing import Any

from workbench_tools import CHECK, PAGE, RUN, SCHEMA

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import project_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.import_tables import publish_imports
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import NativeCapture, capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_log import QueryLog
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.result_delivery import deliver, validate_delivery
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.saved_queries import SavedQueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.service_interface import ServiceInterface
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher import SourceWatcher
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.statements import select_statement
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workspace import WorkspaceStore
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


def create_native_gateway(root: Path, control_root: str, inputs: NativeQueryInputs):
    from direct_gateway import DirectGateway
    from native_project_selection import resolve_native_project

    selection = resolve_native_project(root, control_root, validate_manifest=inputs.validate_manifest)
    return DirectGateway(selection.root, native_query=NativeQueryOwner(selection, inputs))


QUERY_TOOLS = frozenset({RUN, PAGE, CHECK, SCHEMA})
LIFECYCLE_TOOLS = frozenset({
    "atom_lifecycle_direct_update", "atom_lifecycle_create_draft", "atom_lifecycle_change_status",
    "atom_lifecycle_archive", "atom_lifecycle_promote_draft", "atom_lifecycle_update",
})
QUERY_TABLES = frozenset({
    "atoms", "relations", "native_references", "native_legacy_references", "native_migration_paths",
    "import_nodes", "module_imports", "import_edges", "package_imports",
})


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
        self._workspaces = WorkspaceStore(self._root)
        self._query_log = QueryLog(self._root)
        self._interface_lock = threading.RLock()
        self._watcher: SourceWatcher | None = None
        self._import_thread: threading.Thread | None = None
        self._import_stop = threading.Event()
        self._import_sources = {}

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

    def _refresh_imports(
        self, store: QueryStore, roots: tuple[str, ...], include: tuple[str, ...],
        *, changes: list[dict[str, str | None]] | None = None,
    ) -> None:
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import capture
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.resolution import resolve
        sources = capture(self._root, self._import_sources, include, changes=changes)
        nodes, occurrences, edges = resolve(self._root, sources, roots)
        publish_imports(store, nodes, occurrences, edges)
        self._import_sources = sources

    def _watch_imports(self, store: QueryStore, roots: tuple[str, ...], include: tuple[str, ...]) -> None:
        from APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.source import relevant_change

        assert self._watcher is not None
        while not self._import_stop.is_set():
            batch = self._watcher.changes(timeout=0.1)
            try:
                if batch and relevant_change(self._root, batch, self._import_sources):
                    self._refresh_imports(store, roots, include, changes=batch)
            except Exception as error:
                print(f"Import graph refresh failed. Batch discarded. {error}", file=sys.stderr)

    def _project(self, store: QueryStore) -> NativeCapture:
        capture = capture_native(self.selection)
        project_native(store, capture, relation_types=self._inputs.relation_types,
                       inverses=self._inputs.inverses, migration_refs=self._inputs.migration_refs)
        return capture

    def start(self) -> None:
        runtime = self.selection.parameters.get("runtime", {})
        workbench = runtime.get("workbench", {}) if isinstance(runtime, dict) else None
        if not isinstance(workbench, dict):
            raise ValueError("Project Manifest runtime.workbench must be a mapping")
        import_options = self._import_options(workbench)
        options = {key: workbench[key] for key in ("result_ttl_seconds", "schema_mode") if key in workbench}
        store = QueryStore(extension_directory=self._inputs.extension_directory, **options)
        try:
            if import_options is not None:
                self._watcher = SourceWatcher(self._root, self._root / self.selection.control_relative,
                                              implementation_root=self._root)
                self._watcher.start()
            self._capture = self._project(store)
            if import_options is not None:
                self._refresh_imports(store, *import_options)
                self._import_thread = threading.Thread(target=self._watch_imports, args=(store, *import_options),
                                                       name="native-import-graph", daemon=True)
                self._import_thread.start()
        except BaseException:
            if self._watcher is not None:
                self._watcher.close()
                self._watcher = None
            store.close()
            raise
        self._store = store
        self._workspaces.clear_transient_results()

    def _refresh_after_write(self, store: QueryStore) -> None:
        try:
            self._capture = self._project(store)
        except Exception:
            self._capture = None
            with store._lock:
                store._available = False
            raise

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
            rows = self._capture.atoms
            try:
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
                    outcome = create_draft(self.selection, arguments, current_rows=rows)
                elif name == "atom_lifecycle_archive":
                    outcome = archive_ticket(self.selection, arguments, current_rows=rows)
                elif name == "atom_lifecycle_promote_draft":
                    outcome = promote_draft(
                        self.selection, arguments, current_rows=rows, migration_refs=self._inputs.migration_refs,
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
