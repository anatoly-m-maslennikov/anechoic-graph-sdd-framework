"""Workbench interface operations."""

from __future__ import annotations
import sys
from typing import Any
from ._interface_dispatch import InterfaceDispatch
from ..errors import QueryExecutionError, WorkbenchUnavailableError
from ..query_store import QueryStore
from ..result_delivery import (
    deliver,
    validate_delivery,
    result_metadata,
    failed_metadata,
)
from ..saved_queries import SavedQueryStore
from ..statements import select_statement
from ..workspace import WorkspaceStore as WorkspaceStore


class ServiceInterface(InterfaceDispatch):
    def run(
        self,
        sql: str,
        page_size: int = 100,
        cursor_position: int | None = None,
        *,
        save: bool = False,
        preview: int | None = None,
        name: str | None = None,
        result_delivery: str = "file",
        result_format: str = "json_matrix",
    ) -> dict[str, Any]:
        validate_delivery(result_delivery, result_format)
        if type(save) is not bool:
            raise ValueError("save must be a boolean")
        if name is not None and not save:
            raise ValueError("name is only supported when save is true")
        page_size = QueryStore._page_size(page_size)
        preview = QueryStore._preview(preview)
        if save:
            name = SavedQueryStore._name(name)
        selected = select_statement(sql, cursor_position)
        try:
            result = self._run_store(
                selected,
                page_size=page_size,
                preview=preview,
                include_rows=True,
            )
            if save:
                result = self._save_run_result(sql, name, result)
            self._log_attempt(sql, result_metadata(result))
            return self._deliver_run(result, result_delivery, result_format)
        except (
            ValueError,
            QueryExecutionError,
            WorkbenchUnavailableError,
        ) as error:
            self._log_attempt(sql, failed_metadata(error))
            raise

    def _deliver_run(self, result, result_delivery, result_format):
        assert self._store is not None
        return deliver(
            self._store,
            self._root,
            result,
            result_delivery,
            result_format,
            full=True,
        )

    def _save_run_result(self, sql, name, result):
        try:
            result |= self._saved_queries.save_query(sql, name)
        except (ValueError, OSError) as error:
            print(f"saved query failed: {error}", file=sys.stderr)
            result |= {"outcome": "partial", "save_error": str(error)}
        return result

    def _run_store(
        self,
        selected: str,
        *,
        page_size: int = 100,
        preview: int | None = None,
        include_rows: bool,
    ) -> dict[str, Any]:
        self._flush_lifecycle_changes()
        assert self._store is not None
        self._store.prune_results()
        return self._store.run(
            selected,
            page_size=page_size,
            preview=preview,
            include_rows=include_rows,
        )

    def _log_attempt(self, sql: str, metadata: dict[str, Any]) -> None:
        try:
            self._query_log.append_async(sql, metadata)
        except Exception as error:
            print(f"query log failed: {error}", file=sys.stderr)

    def _drop_result(self, query_id: str | None) -> None:
        if query_id is not None and self._store is not None:
            self._store.drop(query_id)

    def _unpin_result(self, query_id: str | None) -> None:
        if query_id is not None and self._store is not None:
            self._store.unpin(query_id)

    def _view_run(self, arguments: object) -> dict[str, Any]:
        args, save, preview = self._view_run_args(arguments)
        current = self._workspaces.get_view(
            args["workspace_id"], args["view_id"]
        )
        selected = select_statement(
            current["sql"], args.get("cursor_position")
        )
        view, prior = self._workspaces.clear_result(
            args["workspace_id"], args["view_id"]
        )
        self._unpin_result(prior)
        self._drop_result(prior)
        try:
            result = self._run_store(
                selected, preview=preview, include_rows=False
            )
            metadata = result_metadata(result)
            assert self._store is not None
            self._store.pin(metadata["query_id"])
            saved: dict[str, Any] = {}
            if save:
                try:
                    saved = self._saved_queries.save_query(
                        current["sql"], args.get("name")
                    )
                except ValueError as error:
                    print(f"saved query failed: {error}", file=sys.stderr)
                    saved = {"save_error": str(error)}
        except WorkbenchUnavailableError:
            raise
        except (QueryExecutionError, ValueError) as error:
            metadata, saved = failed_metadata(error), {}
        return self._complete_view_run(args, view, current, metadata, saved)

    def _complete_view_run(self, args, view, current, metadata, saved):
        self._log_attempt(current["sql"], metadata)
        self._workspaces.set_result(
            args["workspace_id"], args["view_id"], metadata
        )
        return (
            {
                "workspace_id": view["workspace_id"],
                "view_id": view["view_id"],
                "revision": view["revision"],
            }
            | metadata
            | saved
        )

    def _view_run_args(self, arguments):
        args = self._arguments(
            "view_run",
            arguments,
            {
                "workspace_id",
                "view_id",
                "cursor_position",
                "preview",
                "save",
                "name",
            },
            {"workspace_id", "view_id"},
        )
        save = args.get("save", False)
        if type(save) is not bool:
            raise ValueError("save must be a boolean")
        if args.get("name") is not None and not save:
            raise ValueError("name is only supported when save is true")
        preview = QueryStore._preview(args.get("preview"))
        if save:
            SavedQueryStore._name(args.get("name"))
        return args, save, preview

    def _view_fetch(self, arguments: object) -> dict[str, Any]:
        args = self._view_fetch_args(arguments)
        view = self._workspaces.get_view(args["workspace_id"], args["view_id"])
        result = view.get("result")
        if (
            not isinstance(result, dict)
            or result.get("status") != "success"
            or not isinstance(result.get("query_id"), str)
        ):
            raise ValueError("view has no current result")
        page_size = self._limit(args.get("page_size", 100), "page_size")
        preview = QueryStore._preview(args.get("preview"))
        offset = self._offset(args.get("offset", 0))
        self._start()
        assert self._store is not None
        self._store.prune_results()
        page = self._store.page(
            result["query_id"],
            offset,
            page_size=page_size,
            preview=preview,
            grid=args.get("grid"),
        )
        page = deliver(
            self._store,
            self._root,
            page,
            args.get("result_delivery", "file"),
            args.get("result_format", "json_matrix"),
        )
        return {
            "workspace_id": view["workspace_id"],
            "view_id": view["view_id"],
        } | page

    def _view_fetch_args(self, arguments):
        args = self._arguments(
            "view_fetch",
            arguments,
            {
                "workspace_id",
                "view_id",
                "offset",
                "page_size",
                "preview",
                "grid",
                "result_delivery",
                "result_format",
            },
            {"workspace_id", "view_id"},
        )
        if "grid" in args and not isinstance(args["grid"], dict):
            raise ValueError("grid must be an object")
        validate_delivery(
            args.get("result_delivery", "file"),
            args.get("result_format", "json_matrix"),
        )
        return args
