"""Typed View inputs and their public Tool descriptors."""

from typing import Any, Literal

from pydantic import Field, StrictBool, model_validator

from ..CORE.CORE__shared import StrictModel


class Workspace(StrictModel):
    workspace_id: str

    @model_validator(mode="after")
    def valid_workspace(self):
        if not self.workspace_id.strip():
            raise ValueError("Invalid workspace_id")
        return self


class View(Workspace):
    view_id: str

    @model_validator(mode="after")
    def valid_view(self):
        if not self.view_id.strip():
            raise ValueError("Invalid view_id")
        return self


class Create(Workspace):
    name: str | None = None
    position: Literal["first", "last"] | None = None


class Update(View):
    sql: str
    expected_revision: int = Field(ge=0)
    cursor_position: int | None = Field(default=None, ge=0)


class Rename(View):
    name: str


class Check(View):
    cursor_position: int | None = Field(default=None, ge=0)


class Run(Check):
    preview: int | None = Field(default=None, ge=0)
    save: StrictBool = False
    name: str | None = None

    @model_validator(mode="after")
    def valid_save(self):
        if "name" in self.model_fields_set and not self.save:
            raise ValueError("name is only supported when save is true")
        return self


class Fetch(View):
    offset: int | None = Field(default=None, ge=0)
    page_size: int | None = Field(default=None, ge=1, le=1000)
    preview: int | None = Field(default=None, ge=0)
    grid: dict[str, Any] | None = None
    result_delivery: Literal["file", "inline", "auto"] | None = None
    result_format: Literal["json_matrix", "csv", "toon"] | None = None


MODELS = {
    "view_create": Create,
    "view_duplicate": View,
    "view_list": Workspace,
    "view_get": View,
    "view_update": Update,
    "view_focus": View,
    "view_rename": Rename,
    "view_remove": View,
    "view_run": Run,
    "view_check": Check,
    "view_fetch": Fetch,
}


def arguments(name, args):
    if any(value is None for value in args.values()):
        raise ValueError("Null View arguments are not supported")
    fields = MODELS[name].model_validate(args).model_dump(exclude_unset=True)
    for value in fields.values():
        if isinstance(value, str):
            value.encode("utf-8")
    if name == "view_fetch":
        fields = {"result_delivery": "file", **fields}
    return fields


def _grid(number, text):
    order = {
        "type": "object",
        "properties": {
            "column": number,
            "direction": {"type": "string", "enum": ["asc", "desc"]},
        },
        "required": ["column", "direction"],
        "additionalProperties": False,
    }
    filt = {
        "type": "object",
        "properties": {
            "column": number,
            "operator": {"const": "contains"},
            "value": text,
        },
        "required": ["column", "operator", "value"],
        "additionalProperties": False,
    }
    grid = {
        "type": "object",
        "properties": {
            "sort": {"type": "array", "items": order},
            "filters": {"type": "array", "items": filt},
            "group_by": order,
        },
        "additionalProperties": False,
    }
    return grid


def _initial_views(workspace, view, text):
    return {
        "view_create": (
            "Create a stable View in a Workspace.",
            workspace,
            {
                "position": {
                    "type": "string",
                    "enum": ["first", "last"],
                    "default": "last",
                },
                "name": text,
            },
            False,
        ),
        "view_duplicate": (
            (
                "Duplicate one View's query and cursor into a new independent "
                "View."
            ),
            view,
            {},
            False,
        ),
        "view_list": (
            "List ordered Workspace Views and their result metadata.",
            workspace,
            {},
            True,
        ),
        "view_get": (
            "Get one View's SQL, revision, and result metadata without rows.",
            view,
            {},
            True,
        ),
    }


def _edit_views(view, text, number):
    return {
        "view_update": (
            "Update one View using its expected revision.",
            {**view, "sql": text, "expected_revision": number},
            {"cursor_position": number},
            False,
        ),
        "view_focus": (
            "Set the active View for a Workspace.",
            view,
            {},
            False,
        ),
        "view_rename": ("Rename one View.", {**view, "name": text}, {}, False),
        "view_remove": (
            "Remove one View while retaining at least one View.",
            view,
            {},
            False,
        ),
    }


def _run_views(view, text, number):
    return {
        "view_run": (
            "Run one View and return metadata without result rows.",
            view,
            {
                "cursor_position": number,
                "preview": number,
                "save": {"type": "boolean", "default": False},
                "name": text,
            },
            False,
        ),
        "view_check": (
            "Check one View without recording a query log entry.",
            view,
            {"cursor_position": number},
            True,
        ),
    }


def _fetch_views(view, number, size, grid):
    return {
        "view_fetch": (
            "Fetch a page from one View’s current result.",
            view,
            {
                "offset": number,
                "page_size": size,
                "preview": number,
                "grid": grid,
                "result_delivery": {
                    "type": "string",
                    "enum": ["file", "inline", "auto"],
                    "default": "file",
                },
                "result_format": {
                    "type": "string",
                    "enum": ["json_matrix", "csv", "toon"],
                },
            },
            True,
        ),
    }


def descriptors():
    identity, text = {"type": "string", "minLength": 1}, {"type": "string"}
    number = {"type": "integer", "minimum": 0}
    size = {"type": "integer", "minimum": 1, "maximum": 1000}
    grid = _grid(number, text)
    workspace, view = (
        {"workspace_id": identity},
        {"workspace_id": identity, "view_id": identity},
    )
    definitions = {
        **_initial_views(workspace, view, text),
        **_edit_views(view, text, number),
        **_run_views(view, text, number),
        **_fetch_views(view, number, size, grid),
    }
    result = {}
    for name, (
        description,
        required,
        optional,
        read_only,
    ) in definitions.items():
        schema = {
            "type": "object",
            "properties": {**required, **optional},
            "required": list(required),
            "additionalProperties": False,
        }
        result[name] = {
            "name": name,
            "description": description,
            "inputSchema": schema,
            "annotations": {
                "readOnlyHint": read_only,
                "destructiveHint": False,
                "idempotentHint": read_only,
                "openWorldHint": False,
            },
        }
    return result
