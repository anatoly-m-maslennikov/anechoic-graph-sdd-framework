"""Validate and dispatch Workbench operations for one Project."""

from __future__ import annotations

import threading
from typing import Any

from KERNEL_MIXER_C59.errors import QueryExecutionError, WorkbenchUnavailableError
from KERNEL_MIXER_C59.result_delivery import DELIVERY_MODES

RUN, PAGE, CHECK, SCHEMA = "query_run", "query_page", "query_check", "query_schema"
SAVE_VIEW, LOAD, SAVED_LIST = "view_save", "query_load", "query_saved_list"
REBUILD = "query_rebuild"
SYNC_STATUS = "workbench_status"
WORKSPACE_OPEN, WORKSPACE_LIST, WORKSPACE_GET = "workspace_open", "workspace_list", "workspace_get"
VIEW_CREATE, VIEW_DUPLICATE, VIEW_LIST, VIEW_GET, VIEW_UPDATE = (
    "view_create", "view_duplicate", "view_list", "view_get", "view_update"
)
VIEW_RUN, VIEW_CHECK, VIEW_FETCH, VIEW_FOCUS = "view_run", "view_check", "view_fetch", "view_focus"
VIEW_RENAME, VIEW_REMOVE = "view_rename", "view_remove"
QUERY_LOG_LIST, QUERY_LOG_GET = "query_log_list", "query_log_get"
INTERFACE_TOOLS = (
    WORKSPACE_OPEN, WORKSPACE_LIST, WORKSPACE_GET, VIEW_CREATE, VIEW_DUPLICATE, VIEW_LIST, VIEW_GET,
    VIEW_UPDATE, VIEW_RUN, VIEW_CHECK, VIEW_FETCH, VIEW_FOCUS, VIEW_RENAME, VIEW_REMOVE,
    QUERY_LOG_LIST, QUERY_LOG_GET,
)


class WorkbenchOperations:
    """Expose operations on the selected native Project's Workbench."""

    def __init__(self, *, query_owner: Any, lock=None) -> None:
        self._query_owner = query_owner
        self._lock = lock if lock is not None else threading.RLock()

    def call(self, name: str, arguments: Any) -> dict[str, Any]:  # noqa: C901
        if name == SYNC_STATUS:
            self._empty(arguments)
            return self._query_owner.status()
        with self._lock:
            if name == REBUILD:
                return self._rebuild(arguments)
            if name in INTERFACE_TOOLS:
                return self._query_owner.interface_call(name, arguments)
            if name == RUN:
                sql, page_size, cursor, save, preview, query_name, delivery, result_format = self._run(arguments)
                return self._query_owner.run(
                    sql, page_size=page_size, cursor_position=cursor,
                    save=save, preview=preview, name=query_name,
                    result_delivery=delivery, result_format=result_format,
                )
            if name == CHECK:
                sql, cursor = self._sql(arguments, {"sql", "cursor_position"})
                return self._query_owner.check(sql, cursor_position=cursor)
            if name == PAGE:
                query_id, offset, page_size, grid, preview, delivery, result_format = self._page(arguments)
                return self._query_owner.page(
                    query_id, offset, page_size=page_size, grid=grid, preview=preview,
                    result_delivery=delivery, result_format=result_format,
                )
            if name == SCHEMA:
                self._empty(arguments)
                return self._query_owner.schema()
            if name == SAVE_VIEW:
                if isinstance(arguments, dict) and {"workspace_id", "view_id"} <= set(arguments):
                    return self._query_owner.interface_call(name, arguments)
                sql, _ = self._sql(arguments, {"sql", "name"})
                return self._query_owner.save_view(sql, name=self._name(arguments))
            if name == LOAD:
                reference, _ = self._sql(arguments, {"reference"}, key="reference")
                return self._query_owner.load(reference)
            if name == SAVED_LIST:
                return self._query_owner.saved_list(limit=self._limit(arguments))
            raise ValueError("Unknown Workbench tool")

    def _rebuild(self, arguments):
        if not isinstance(arguments, dict) or set(arguments) != {"target"} or not isinstance(arguments["target"], str) or not arguments["target"].strip():
            raise ValueError("Expected a non-empty target table selector or all")
        try:
            return self._query_owner.rebuild(arguments["target"])
        except (ValueError, QueryExecutionError, WorkbenchUnavailableError):
            raise
        except Exception as error:
            raise QueryExecutionError("Query rebuild failed. See process diagnostics.") from error

    @staticmethod
    def _sql(arguments: Any, allowed: set[str], *, key: str = "sql") -> tuple[str, int | None]:
        if not isinstance(arguments, dict) or set(arguments) - allowed or key not in arguments:
            raise ValueError(f"Expected only {' and '.join(sorted(allowed))}")
        value, cursor = arguments[key], arguments.get("cursor_position")
        if not isinstance(value, str):
            raise ValueError(f"{key} must be a string")
        if cursor is not None and (isinstance(cursor, bool) or not isinstance(cursor, int) or cursor < 0):
            raise ValueError("cursor_position must be a non-negative integer")
        return value, cursor

    @staticmethod
    def _page_size(arguments: dict[str, Any], default: int = 100) -> int:
        value = arguments.get("page_size", default)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("page_size must be an integer")
        if not 1 <= value <= 1000:
            raise ValueError("page_size must be between 1 and 1000")
        return value

    @staticmethod
    def _name(arguments: dict[str, Any]) -> str | None:
        value = arguments.get("name")
        if value is not None and not isinstance(value, str):
            raise ValueError("name must be a string")
        return value

    @staticmethod
    def _result_options(arguments: dict[str, Any]) -> tuple[int | None, str, str]:
        preview = arguments.get("preview")
        if preview is not None and (isinstance(preview, bool) or not isinstance(preview, int) or preview < 0):
            raise ValueError("preview must be a non-negative integer")
        delivery = arguments.get("result_delivery", "file")
        if delivery not in DELIVERY_MODES:
            raise ValueError("result_delivery must be file, inline or auto")
        result_format = arguments.get("result_format", "json_matrix")
        if not isinstance(result_format, str) or result_format not in {"json_matrix", "csv", "toon"}:
            raise ValueError("result_format must be json_matrix, csv or toon")
        return preview, delivery, result_format

    def _run(self, arguments: Any) -> tuple[str, int, int | None, bool, int | None, str | None, str, str]:
        sql, cursor = self._sql(arguments, {"sql", "page_size", "cursor_position", "save", "preview", "name", "result_delivery", "result_format"})
        save = arguments.get("save", False)
        if type(save) is not bool:
            raise ValueError("save must be a boolean")
        preview, delivery, result_format = self._result_options(arguments)
        if "name" in arguments and not isinstance(arguments["name"], str):
            raise ValueError("name must be a string")
        query_name = arguments.get("name")
        if query_name is not None and not save:
            raise ValueError("name is only valid when save is true")
        page_size_default = 1000 if delivery == "auto" and result_format != "toon" else 100
        return sql, self._page_size(arguments, page_size_default), cursor, save, preview, query_name, delivery, result_format

    def _page(self, arguments: Any) -> tuple[str, int, int, Any, int | None, str, str]:
        allowed = {"query_id", "offset", "page_size", "grid", "preview", "result_delivery", "result_format"}
        if not isinstance(arguments, dict) or set(arguments) - allowed or "query_id" not in arguments:
            raise ValueError("Expected query_id and optional pagination, grid and result options")
        if "grid" in arguments and not isinstance(arguments["grid"], dict):
            raise ValueError("grid must be an object")
        query_id, offset = arguments["query_id"], arguments.get("offset", 0)
        if not isinstance(query_id, str):
            raise ValueError("query_id must be a string")
        if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
            raise ValueError("offset must be a non-negative integer")
        preview, delivery, result_format = self._result_options(arguments)
        return query_id, offset, self._page_size(arguments), arguments.get("grid"), preview, delivery, result_format

    @staticmethod
    def _empty(arguments: Any) -> None:
        if arguments != {}:
            raise ValueError("Expected an empty object")

    @staticmethod
    def _limit(arguments: Any) -> int:
        if not isinstance(arguments, dict) or set(arguments) - {"limit"}:
            raise ValueError("Expected optional limit")
        value = arguments.get("limit", 20)
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 1000:
            raise ValueError("limit must be an integer from 1 to 1000")
        return value

    def close(self) -> None:
        with self._lock:
            self._query_owner.close()

