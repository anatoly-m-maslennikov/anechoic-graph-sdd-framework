"""Serve an explicitly selected native Project's startup snapshot through Workbench."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp import types
from workbench_tools import CHECK, PAGE, RUN, SCHEMA

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_projection import project_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.query_store import QueryStore
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.result_delivery import deliver, validate_delivery
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.statements import select_statement
from native_project_selection import ManifestIdentity, NativeProjectSelection


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


QUERY_TOOLS = frozenset({RUN, PAGE, CHECK, SCHEMA})
QUERY_TABLES = frozenset({
    "atoms", "relations", "native_references", "native_legacy_references", "native_migration_paths",
})


def query_tool(tool: types.Tool) -> types.Tool:
    if tool.name != RUN:
        return tool
    properties = dict(tool.input_schema["properties"])
    properties.pop("name")
    properties["save"] = {"type": "boolean", "const": False, "default": False}
    return tool.model_copy(update={
        "input_schema": {**tool.input_schema, "properties": properties},
        "annotations": tool.annotations.model_copy(update={"read_only_hint": True, "idempotent_hint": False}),
    })


class NativeQueryOwner:
    def __init__(self, selection: NativeProjectSelection, inputs: NativeQueryInputs) -> None:
        self.selection = selection
        self._inputs = inputs
        self._store: QueryStore | None = None

    def start(self) -> None:
        capture = capture_native(self.selection)
        store = QueryStore(extension_directory=self._inputs.extension_directory)
        try:
            project_native(store, capture, relation_types=self._inputs.relation_types,
                           inverses=self._inputs.inverses, migration_refs=self._inputs.migration_refs)
        except BaseException:
            store.close()
            raise
        self._store = store

    def _owner(self) -> QueryStore:
        if self._store is None:
            raise RuntimeError("Native query projection is unavailable")
        return self._store

    def run(self, sql: str, page_size: int = 100, cursor_position: int | None = None, *,
            save: bool = False, preview: int | None = None, name: str | None = None,
            result_delivery: str = "file", result_format: str = "json_matrix") -> dict[str, Any]:
        if save or name is not None:
            raise ValueError("Native queries cannot save Bookmarks")
        validate_delivery(result_delivery, result_format)
        store = self._owner()
        store.prune_results()
        result = store.run(select_statement(sql, cursor_position), page_size=page_size, preview=preview)
        return deliver(store, self.selection.root, result, result_delivery, result_format, full=True)

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
        if self._store is not None:
            self._store.close()
            self._store = None
