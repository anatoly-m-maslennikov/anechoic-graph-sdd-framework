"""Serve an explicitly selected native Project's startup snapshot through Workbench."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
import threading
from typing import Any

from workbench_tools import CHECK, PAGE, RUN, SCHEMA

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import project_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_log import QueryLog
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.result_delivery import deliver, validate_delivery
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.saved_queries import SavedQueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.service_interface import ServiceInterface
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
QUERY_TABLES = frozenset({
    "atoms", "relations", "native_references", "native_legacy_references", "native_migration_paths",
})


class NativeQueryOwner(ServiceInterface):
    def __init__(self, selection: NativeProjectSelection, inputs: NativeQueryInputs) -> None:
        self.selection = selection
        self._root = selection.root
        self._inputs = inputs
        self._store: QueryStore | None = None
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

    def start(self) -> None:
        capture = capture_native(self.selection)
        runtime = self.selection.parameters.get("runtime", {})
        workbench = runtime.get("workbench", {}) if isinstance(runtime, dict) else None
        if not isinstance(workbench, dict):
            raise ValueError("Project Manifest runtime.workbench must be a mapping")
        options = {key: workbench[key] for key in ("result_ttl_seconds", "schema_mode") if key in workbench}
        store = QueryStore(extension_directory=self._inputs.extension_directory, **options)
        try:
            project_native(store, capture, relation_types=self._inputs.relation_types,
                           inverses=self._inputs.inverses, migration_refs=self._inputs.migration_refs)
        except BaseException:
            store.close()
            raise
        self._store = store
        self._workspaces.clear_transient_results()

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
        if self._store is None:
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
        self._query_log.close()
        if self._store is not None:
            self._store.close()
            self._store = None
