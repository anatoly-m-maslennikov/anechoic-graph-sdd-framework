"""Encode source Atom rows and their canonical representation."""

from collections.abc import Mapping
import datetime as dt
import json
from pathlib import Path
import re
from typing import Any, Literal

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    markdown_content__pub import (
    parse_content,
    summary_title,
)
# fmt: on


def json_value(value: Any) -> Any:
    """Represent admitted YAML values without changing their source Header."""
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("JSON mapping keys must be strings")
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return value


def canonical(value: Any) -> str:
    return json.dumps(
        json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


_NUMBERED_DRAFT_REFERENCE = re.compile(r"@\d+-draft$")


def _reference(
    atom_id: Any, version: Any, explicit: Any, group: str, source_path: str
) -> str | None:
    if not isinstance(atom_id, str):
        return None
    if group in {"Current", "Backlog"}:
        return atom_id
    if group == "Draft" and type(version) is int:
        if _NUMBERED_DRAFT_REFERENCE.search(atom_id):
            return atom_id
        if atom_id.endswith(("-draft", "@draft")):
            return f"{atom_id}:{source_path}"
        return f"{atom_id}@{version}-draft"
    if group == "Archived":
        if isinstance(explicit, str) and re.search(r"@[1-9][0-9]*$", explicit):
            return explicit
        if (
            not re.search(r"@[1-9][0-9]*$", atom_id)
            and type(version) is int
            and version > 0
        ):
            return f"{atom_id}@{version}"
        return atom_id
    return None


def atom(
    path: Path,
    root: Path,
    header: dict[str, Any],
    view: dict[str, Any],
    body: str | bytes,
    group: str,
    *,
    include_content_properties: bool | Literal["summary"] = True,
) -> dict[str, Any]:
    cached_body = body.encode("utf-8") if isinstance(body, str) else body
    if not isinstance(cached_body, bytes):
        raise TypeError("Markdown body must be UTF-8 text or bytes")
    atom_id, version = view.get("atom_id"), view.get("version")
    source_path = path.relative_to(root).as_posix()
    row = {
        "source_path": source_path,
        "status_group": group,
        "id": atom_id if isinstance(atom_id, str) else None,
        "ref": _reference(
            atom_id, version, view.get("ref_id"), group, source_path
        ),
        "version": bigint(version),
        "status": string(view.get("status")),
        "current_scope_unit": string(header.get("current_scope_unit")),
        "claim_target_scope_unit": string(
            header.get("claim_target_scope_unit")
        ),
        "role": string(view.get("content_role")),
        "form": string(view.get("type")),
        "tier": bigint(view.get("tier")),
        "updated_at": view.get("updated_at"),
        "header_json": header,
        "_content_bytes": cached_body,
        "content_properties_json": _content_properties(
            cached_body, include_content_properties
        ),
        "relation_edges_json": [],
        "hash": None,
    }
    if include_content_properties == "summary":
        row["_summary_title"] = summary_title(cached_body)
    return row


def _content_properties(cached_body, include_content_properties):
    return (
        parse_content(
            cached_body.decode("utf-8"),
            tolerate_duplicate_siblings=True,
            compact=True,
        )
        if include_content_properties is True
        else []
    )


def string(value: Any) -> str | None:
    return value if isinstance(value, str) else None


def bigint(value: Any) -> int | None:
    return value if type(value) is int and -(2**63) <= value < 2**63 else None


def canonical_row(row: Mapping[str, Any]) -> str:
    """Validate a source row without decoding its private cached body."""
    payload = dict(row)
    if "_content_bytes" in payload:
        body = payload.pop("_content_bytes")
        if not isinstance(body, bytes):
            raise TypeError("cached Markdown body must be UTF-8 bytes")
    return canonical(payload)
