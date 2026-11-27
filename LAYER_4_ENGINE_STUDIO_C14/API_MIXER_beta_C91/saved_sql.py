"""Project-bound saved SQL requests and public Workbench links."""

import re
from typing import Literal
from urllib.parse import parse_qs, quote, urlencode, urlparse
from uuid import UUID

import httpx2
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .admission import failure, peer
from .projection import PeerError


_IWE_CONSOLE_PATH = "/anechoic/iwe-console"
_LEGACY_WORKBENCH_PATH = "/anechoic/workbench"


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")


class LinkContext(StrictModel):
    project_name: str | None = None
    base: str | None = None
    root: str | None = None
    configured_url: str | None = None


class Load(StrictModel):
    reference: str


class Listing(StrictModel):
    limit: int = Field(default=20, ge=1, le=1000)


class ViewSql(StrictModel):
    sql: str
    name: str | None = None


class ViewIds(StrictModel):
    workspace_id: str
    view_id: str

    @model_validator(mode="after")
    def nonblank(self):
        if not self.workspace_id.strip() or not self.view_id.strip():
            raise ValueError("Invalid View IDs")
        return self


class Record(StrictModel):
    saved_query_id: str
    kind: Literal["query", "view"]
    sql: str
    name: str | None = None
    saved_at: str | None = None

    @model_validator(mode="after")
    def valid_record(self):
        if not saved_id(self.saved_query_id) or any(
            getattr(self, key) is None for key in self.model_fields_set
        ):
            raise ValueError("Invalid saved query record")
        return self


class ListedRecord(StrictModel):
    saved_query_id: str
    kind: Literal["query", "view"]
    preview: str
    saved_at: str
    name: str | None = None

    @model_validator(mode="after")
    def valid_record(self):
        if not saved_id(self.saved_query_id) or (
            "name" in self.model_fields_set and self.name is None
        ):
            raise ValueError("Invalid saved query record")
        return self


class SavedItems(StrictModel):
    items: list[ListedRecord]


def _save_schema():
    return [
        {
            "required": ["workspace_id", "view_id"],
            "not": {
                "anyOf": [
                    {"required": ["sql"]},
                    {"required": ["name"]},
                ]
            },
        },
        {
            "required": ["sql"],
            "not": {
                "anyOf": [
                    {"required": ["workspace_id"]},
                    {"required": ["view_id"]},
                ]
            },
        },
    ]


def _descriptor(name, description, properties, read_only):
    schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if name == "query_load":
        schema["required"] = ["reference"]
    if name == "view_save":
        schema["oneOf"] = _save_schema()
    return {
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


def descriptors():
    text = {"type": "string"}
    identity = {"type": "string", "minLength": 1}
    definitions = {
        "query_load": (
            "Load a Bookmark or saved View.",
            {"reference": text},
            True,
        ),
        "query_saved_list": (
            "List recent Bookmark and saved View metadata.",
            {"limit": {"type": "integer", "minimum": 1, "maximum": 1000}},
            True,
        ),
        "view_save": (
            "Save a View's exact SQL without executing it.",
            {
                "workspace_id": identity,
                "view_id": identity,
                "sql": text,
                "name": text,
            },
            False,
        ),
    }
    tools = {}
    for name, (description, properties, read_only) in definitions.items():
        tools[name] = _descriptor(name, description, properties, read_only)
    return tools


def new_id(value):
    try:
        parsed = UUID(value)
        return parsed.version == 7 and str(parsed) == value
    except ValueError, TypeError, AttributeError:
        return False


def saved_id(value):
    return isinstance(value, str) and (
        re.fullmatch(r"[qw]_[0-9a-f]{32}", value) is not None or new_id(value)
    )


def public_page(context):
    name, base, configured = (
        context.project_name,
        context.base,
        context.configured_url,
    )
    if base is not None:
        return (
            f"{base.rstrip('/')}{_IWE_CONSOLE_PATH}/{quote(name, safe='')}"
            if name and base
            else None
        )
    if (
        not configured
        or any(
            char.isspace() or ord(char) < 32 or ord(char) == 127
            for char in configured
        )
        or "?" in configured
        or "#" in configured
    ):
        return None
    try:
        parsed = urlparse(configured)
        _ = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or not parsed.path
        or parsed.username is not None
        or parsed.password is not None
        or parsed.params
    ):
        return None
    return configured


def link(item, context):
    page = public_page(context)
    if page is None:
        return {
            **item,
            "saved_query_url": None,
            "saved_query_url_reason": "workbench_url_unknown",
        }
    query = {"query": item["saved_query_id"]}
    if context.root is not None:
        query["project_root"] = context.root
    return {**item, "saved_query_url": f"{page}?{urlencode(query)}"}


def reference(value, context):
    if saved_id(value):
        return value
    if not context.base or not context.project_name:
        raise ValueError(
            "saved query reference must be an ID or this Project's URL"
        )
    parsed = urlparse(value)
    query = parse_qs(parsed.query, keep_blank_values=True)
    name = quote(context.project_name, safe="")
    expected_paths = {
        f"{_IWE_CONSOLE_PATH}/{name}",
        f"{_LEGACY_WORKBENCH_PATH}/{name}",
    }
    if (
        f"{parsed.scheme}://{parsed.netloc}" != context.base.rstrip("/")
        or parsed.path not in expected_paths
        or parsed.params
        or parsed.fragment
        or set(query) - {"query", "project_root"}
        or len(query.get("query", [])) != 1
        or (
            "project_root" in query and query["project_root"] != [context.root]
        )
        or not saved_id(query["query"][0])
    ):
        raise ValueError("saved query URL is not for this Project")
    return query["query"][0]


def arguments(name, args, context):
    if any(value is None for value in args.values()):
        raise ValueError("Null saved query arguments")
    if name == "query_load":
        return {
            "reference": reference(
                Load.model_validate(args).reference, context
            )
        }
    if name == "query_saved_list":
        return Listing.model_validate(args).model_dump(exclude_unset=True)
    model = ViewIds if set(args) == {"workspace_id", "view_id"} else ViewSql
    value = model.model_validate(args).model_dump(exclude_unset=True)
    for item in value.values():
        item.encode("utf-8")
    return value


def present_run(value, args, context):
    if "saved_query_id" not in value:
        if (
            value.get("outcome") != "partial"
            or not isinstance(value.get("save_error"), str)
            or not value["save_error"]
        ):
            raise ValueError("Invalid saved query response")
        return value
    if not new_id(value["saved_query_id"]) or "save_error" in value:
        raise ValueError("Invalid saved query response")
    name = args.get("name", "")
    return link(
        {**value, "kind": "query", **({"name": name} if name.strip() else {})},
        context,
    )


def present(name, value, fields, context):
    if name == "query_saved_list":
        SavedItems.model_validate(value)
        return {"items": [link(item, context) for item in value["items"]]}
    record = Record.model_validate(value)
    if name == "view_save":
        if (
            record.kind != "view"
            or "saved_at" not in record.model_fields_set
            or not new_id(record.saved_query_id)
        ):
            raise ValueError("Invalid saved query response")
        value = value | {
            key: fields[key]
            for key in ("workspace_id", "view_id")
            if key in fields
        }
    return link(value, context)


async def invoke(name, args, database, instance, context):
    try:
        fields = arguments(name, args, context)
    except ValueError, TypeError, UnicodeError:
        return failure("tool_input_invalid", "Invalid saved query arguments")
    try:
        result = await peer(
            database,
            "POST",
            "/workspace",
            json={
                "instance_id": instance,
                "operation": name,
                "arguments": fields,
            },
        )
        if "error" in result:
            error = PeerError.model_validate(result["error"])
            return failure(error.code, error.message)
        return {
            "result": {
                "value": present(name, result["result"], fields, context),
                "text": None,
            }
        }
    except httpx2.HTTPError, ValueError, TypeError, KeyError, UnicodeError:
        return failure(
            "workbench_unavailable", "Saved query service unavailable"
        )
