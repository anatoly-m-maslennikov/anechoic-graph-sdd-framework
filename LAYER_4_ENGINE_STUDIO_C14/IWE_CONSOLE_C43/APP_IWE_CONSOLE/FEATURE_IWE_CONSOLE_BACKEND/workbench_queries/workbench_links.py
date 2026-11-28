"""Public links for persisted Workbench queries."""

from __future__ import annotations

from collections.abc import Mapping
import re
import uuid
from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urlparse

IWE_CONSOLE_PATH = "/anechoic/iwe-console"
_LEGACY_WORKBENCH_PATH = "/anechoic/workbench"

_LEGACY_SAVED_ID = re.compile(r"^[qw]_[0-9a-f]{32}$")


def _saved_id(value: str) -> bool:
    if _LEGACY_SAVED_ID.fullmatch(value):
        return True
    try:
        parsed = uuid.UUID(value)
    except ValueError:
        return False
    return parsed.version == 7 and parsed.variant == uuid.RFC_4122


def project_name(selection: Any) -> str:
    name = getattr(selection, "project_name", None)
    if not isinstance(name, str) or not name:
        raise ValueError("Workbench Project name is unavailable")
    return name


def _saved_page(request: Any, selection: Any) -> str | None:
    base_url = getattr(request, "base_url", None)
    if base_url is not None:
        return (
            f"{str(base_url).rstrip('/')}"
            f"{IWE_CONSOLE_PATH}"
            "/"
            f"{quote(project_name(selection), safe='')}"
        )
    try:
        document = selection.parameters.get("runtime", {})
        page = document.get("workbench", {}).get("public_url")
        if (
            not isinstance(page, str)
            or not page
            or any(c.isspace() or ord(c) < 32 for c in page)
        ):
            return None
        parsed = urlparse(page)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or not parsed.path
            or parsed.params
            or parsed.query
            or parsed.fragment
        ):
            return None
        _ = parsed.port
        return page
    except AttributeError, TypeError, ValueError:
        return None


def public_saved(
    value: Any, request: Any, selection: Any, project_root: str | None = None
) -> Any:
    "Attach a known Workbench URL, or explain why only the saved ID is available."
    if not isinstance(value, Mapping):
        return value
    items = value.get("items")
    if not isinstance(value.get("saved_query_id"), str) and not isinstance(
        items, list
    ):
        return value
    page = _saved_page(request, selection)

    def linked(item: Any) -> Any:
        if not isinstance(item, Mapping) or not isinstance(
            item.get("saved_query_id"), str
        ):
            return item
        if page is None:
            return {
                **item,
                "saved_query_url": None,
                "saved_query_url_reason": "workbench_url_unknown",
            }
        query = {"query": item["saved_query_id"]}
        if project_root is not None:
            query["project_root"] = project_root
        return {**item, "saved_query_url": f"{page}?{urlencode(query)}"}

    result = linked(value)
    if isinstance(items, list):
        result = {**result, "items": [linked(item) for item in items]}
    return result


def public_workspace(
    value: Any, request: Any, selection: Any, project_root: str | None = None
) -> Any:
    "Attach the request-derived URL for one explicitly addressed Workspace."
    if not isinstance(value, Mapping) or not isinstance(
        value.get("workspace_id"), str
    ):
        return value
    base_url = getattr(request, "base_url", None)
    if base_url is None:
        raise ValueError("Workbench public URL requires an HTTP request")
    query = {"workspace": value["workspace_id"]}
    if project_root is not None:
        query["project_root"] = project_root
    name = project_name(selection)
    path = f"{IWE_CONSOLE_PATH}/{quote(name, safe='')}"
    return {
        **value,
        "project_name": name,
        "workspace_url": (
            f"{str(base_url).rstrip('/')}{path}?{urlencode(query)}"
        ),
    }


def context_project_root(context: Any) -> str | None:
    params = getattr(context, "params", None)
    arguments = getattr(params, "arguments", None)
    if not isinstance(arguments, Mapping) and isinstance(params, Mapping):
        arguments = params.get("arguments")
    root = (
        arguments.get("project_root")
        if isinstance(arguments, Mapping)
        else None
    )
    return root if isinstance(root, str) else None


def validate_reference(
    reference: str,
    request: Any,
    selection: Any,
    project_root: str | None = None,
) -> str:
    "Accept a saved ID or this exact Project's public URL, never another Project's URL."
    parsed = urlparse(reference)
    if _saved_id(reference):
        return reference
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("saved query reference must be an ID or absolute URL")
    base_url = getattr(request, "base_url", None)
    if base_url is None:
        raise ValueError("saved query URL requires an HTTP request")
    expected_base = str(base_url).rstrip("/")
    name = quote(project_name(selection), safe="")
    expected_paths = {
        f"{IWE_CONSOLE_PATH}/{name}",
        f"{_LEGACY_WORKBENCH_PATH}/{name}",
    }
    query = parse_qs(parsed.query, keep_blank_values=True)
    if (
        f"{parsed.scheme}://{parsed.netloc}" != expected_base
        or parsed.path not in expected_paths
        or parsed.params
        or parsed.fragment
        or set(query) - {"query", "project_root"}
        or len(query.get("query", [])) != 1
        or (
            "project_root" in query and query["project_root"] != [project_root]
        )
    ):
        raise ValueError("saved query URL is not for this Project")
    return reference
