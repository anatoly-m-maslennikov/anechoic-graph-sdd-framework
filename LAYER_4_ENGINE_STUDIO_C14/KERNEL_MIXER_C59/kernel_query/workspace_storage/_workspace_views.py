"""Workspace documents and their public view representations."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceView(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")

    id: str
    sql: str
    cursor_position: int
    revision: int
    name: str | None = None
    result: dict[str, Any] | None = None


class WorkspaceDocument(BaseModel):
    model_config = ConfigDict(strict=True, extra="allow")

    workspace_id: str
    project_root: str
    active_view_id: str
    views: list[WorkspaceView] = Field(min_length=1)


class _WorkspaceViews:
    @staticmethod
    def _view(document: WorkspaceDocument, view_id: object) -> WorkspaceView:
        if not isinstance(view_id, str) or not view_id:
            raise ValueError("view_id must be a non-empty string")
        for view in document.views:
            if view.id == view_id:
                return view
        raise ValueError("unknown view_id")

    @staticmethod
    def _public_view(view: WorkspaceView, sql: bool) -> dict[str, Any]:
        value = {
            "id": view.id,
            "cursor_position": view.cursor_position,
            "revision": view.revision,
        }
        if "name" in view.model_fields_set:
            value["name"] = view.name
        if sql:
            value["sql"] = view.sql
        if view.result is not None:
            value["result"] = dict(view.result)
        return value

    def _state(self, document: WorkspaceDocument) -> dict[str, Any]:
        return {
            "workspace_id": document.workspace_id,
            "project_root": document.project_root,
            "active_view_id": document.active_view_id,
            "views": [
                self._public_view(view, True) for view in document.views
            ],
        }

    @staticmethod
    def text(
        value: object, field: str, *, required: bool = True
    ) -> str | None:
        if value is None and not required:
            return None
        if not isinstance(value, str) or required and not value.strip():
            raise ValueError(
                f"{field} must be a non-empty string"
                if required
                else f"{field} must be a string"
            )
        try:
            value.encode("utf-8")
        except UnicodeEncodeError as error:
            raise ValueError(f"{field} must be valid UTF-8") from error
        return value

    @staticmethod
    def cursor(value: object) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError("cursor_position must be a non-negative integer")
        return value

    @staticmethod
    def revision(value: object) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(
                "expected_revision must be a non-negative integer"
            )
        return value
