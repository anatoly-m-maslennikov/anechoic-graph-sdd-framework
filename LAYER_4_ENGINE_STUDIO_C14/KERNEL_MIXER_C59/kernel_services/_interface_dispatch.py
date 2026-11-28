"""Validate and dispatch Workspace and View operations."""

from __future__ import annotations

from typing import Any

from . import service_interface as runtime


class InterfaceDispatch:
    @staticmethod
    def _arguments(
        name: str,
        arguments: object,
        allowed: set[str],
        required: set[str] | frozenset[str] = frozenset(),
    ) -> dict[str, Any]:
        if (
            not isinstance(arguments, dict)
            or set(arguments) - allowed
            or required - set(arguments)
        ):
            raise ValueError(f"invalid {name} arguments")
        return arguments

    @staticmethod
    def _limit(value: object, field: str = "limit") -> int:
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 1 <= value <= 1000
        ):
            raise ValueError(f"{field} must be an integer from 1 to 1000")
        return value

    @staticmethod
    def _offset(value: object) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("offset must be a non-negative integer")
        return value

    def _interface_setup(self, name: str, arguments: object) -> dict[str, Any]:
        if name == "workspace_open":
            args = self._arguments(
                name, arguments, {"session_id"}, {"session_id"}
            )
            return self._workspaces.open(args["session_id"])
        if name == "workspace_list":
            self._arguments(name, arguments, set())
            return self._workspaces.list()
        if name == "workspace_get":
            args = self._arguments(
                name, arguments, {"workspace_id"}, {"workspace_id"}
            )
            return self._workspaces.get(args["workspace_id"])
        if name in {"view_create", "view_duplicate", "view_list"}:
            return self._create_or_list_view(name, arguments)
        return self._existing_view_setup(name, arguments)

    def _existing_view_setup(self, name, arguments):
        if name == "view_get":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id"},
                {"workspace_id", "view_id"},
            )
            return self._workspaces.get_view(
                args["workspace_id"], args["view_id"]
            )
        if name == "view_update":
            args = self._arguments(
                name,
                arguments,
                {
                    "workspace_id",
                    "view_id",
                    "sql",
                    "cursor_position",
                    "expected_revision",
                },
                {"workspace_id", "view_id", "sql", "expected_revision"},
            )
            if "cursor_position" in args:
                runtime.WorkspaceStore.cursor(args["cursor_position"])
            return self._workspaces.update(
                args["workspace_id"],
                args["view_id"],
                args["sql"],
                args["expected_revision"],
                args.get("cursor_position"),
            )

    def _create_or_list_view(self, name, arguments):
        if name == "view_create":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "position", "name"},
                {"workspace_id"},
            )
            return self._workspaces.create(
                args["workspace_id"],
                args.get("position", "last"),
                args.get("name"),
            )
        if name == "view_duplicate":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id"},
                {"workspace_id", "view_id"},
            )
            return self._workspaces.duplicate(
                args["workspace_id"], args["view_id"]
            )
        if name == "view_list":
            args = self._arguments(
                name, arguments, {"workspace_id"}, {"workspace_id"}
            )
            return self._workspaces.list_views(args["workspace_id"])

    def interface_call(self, name: str, arguments: object) -> dict[str, Any]:
        """Perform one strictly validated Workspace/View action."""
        with self._interface_lock:
            if name in {
                "workspace_open",
                "workspace_list",
                "workspace_get",
                "view_create",
                "view_duplicate",
                "view_list",
                "view_get",
                "view_update",
            }:
                return self._interface_setup(name, arguments)
            if name == "view_run":
                return self._view_run(arguments)
            if name == "view_fetch":
                return self._view_fetch(arguments)
            if name in {
                "view_check",
                "view_focus",
                "view_rename",
                "view_remove",
                "view_save",
            }:
                return self._interface_view(name, arguments)
            if name == "query_log_list":
                args = self._arguments(name, arguments, {"limit"})
                return self._query_log.list(args.get("limit", 20))
            if name == "query_log_get":
                args = self._arguments(name, arguments, {"log_id"}, {"log_id"})
                return self._query_log.get(args["log_id"])
            raise ValueError("unknown Workbench interface operation")

    def _interface_view(self, name, arguments):
        if name == "view_check":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id", "cursor_position"},
                {"workspace_id", "view_id"},
            )
            view = self._workspaces.get_view(
                args["workspace_id"], args["view_id"]
            )
            return {
                "workspace_id": view["workspace_id"],
                "view_id": view["view_id"],
            } | self.check(view["sql"], args.get("cursor_position"))
        if name == "view_focus":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id"},
                {"workspace_id", "view_id"},
            )
            return self._workspaces.focus(
                args["workspace_id"], args["view_id"]
            )
        return self._edit_view(name, arguments)

    def _edit_view(self, name, arguments):
        if name == "view_rename":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id", "name"},
                {"workspace_id", "view_id", "name"},
            )
            return self._workspaces.rename(
                args["workspace_id"], args["view_id"], args["name"]
            )
        if name == "view_remove":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id"},
                {"workspace_id", "view_id"},
            )
            response, query_id = self._workspaces.remove(
                args["workspace_id"], args["view_id"]
            )
            self._unpin_result(query_id)
            return response
        if name == "view_save":
            args = self._arguments(
                name,
                arguments,
                {"workspace_id", "view_id"},
                {"workspace_id", "view_id"},
            )
            view = self._workspaces.get_view(
                args["workspace_id"], args["view_id"]
            )
            return {
                "workspace_id": view["workspace_id"],
                "view_id": view["view_id"],
            } | self.save_view(view["sql"], view.get("name"))
