"""Shared validation and formatting for declaration views."""

from __future__ import annotations

import json
from collections.abc import Mapping


_METADATA_FIELDS = (
    ("meaning", "Meaning"),
    ("direction", "Declared direct direction"),
    ("inverse", "Inverse direction"),
    ("authority_effect", "Authority effect"),
    ("transitivity", "Transitivity"),
    ("applicability", "Applicability"),
    ("status", "Status"),
    ("exclusive_purpose", "Exclusive purpose"),
)
_UNAVAILABLE = "unavailable (not evidenced in selected authority)"


def _record(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a plain mapping")
    return value


def _required_text(value: object, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or any(char in value for char in "\r\n\t")
    ):
        raise ValueError(f"Invalid {field}")
    return value


def _source_id(value: object) -> str | None:
    if value is None:
        return None
    source = _record(value, "source")
    atom_id = source.get("atom_id")
    version = source.get("version")
    if (
        not isinstance(atom_id, str)
        or not atom_id.strip()
        or isinstance(version, bool)
        or not isinstance(version, int)
        or version < 1
    ):
        raise ValueError("Invalid SourceRef")
    return f"{atom_id.strip()}@{version}"


def _source_ids(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("sources must be a list")
    return sorted({_source_id(item) for item in value if item is not None})


def _display(value: object, unavailable: str = _UNAVAILABLE) -> str:
    if value is None:
        return unavailable
    if isinstance(value, str):
        if not value:
            return unavailable
        return value.replace("\r", "\\r").replace("\n", "\\n")
    if isinstance(value, Mapping):
        normalized = {str(key): item for key, item in value.items()}
        return json.dumps(
            normalized,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
    if isinstance(value, list):
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
    return str(value)


def _metadata(row: dict[str, object]) -> dict[str, object]:
    value = row.get("metadata")
    if value is None:
        return {}
    return _record(value, "metadata")


def _relation_type_lines(row: dict[str, object]) -> list[str]:
    graph_kind = _display(row.get("graph_kind"))
    canonical_name = _display(row.get("canonical_name"))
    metadata = _metadata(row)
    lines = [f"Relation Type: {graph_kind} / {canonical_name}"]
    lines.extend(
        (
            f"\tOwning graph kind: {graph_kind}",
            f"\tCanonical name: {canonical_name}",
        )
    )
    for key, label in _METADATA_FIELDS:
        lines.append(f"\t{label}: {_display(metadata.get(key))}")
    source_ids = _source_ids(row.get("sources"))
    if source_ids:
        lines.append("\tSources:")
        lines.extend(f"\t\t{source_id}" for source_id in source_ids)
    else:
        lines.append(f"\tSources: {_UNAVAILABLE}")
    return lines


def _relation_type_key(row: object) -> tuple[str, str, str]:
    mapped = _record(row, "relation type")
    return (
        _display(mapped.get("graph_kind")),
        _display(mapped.get("canonical_name")),
        json.dumps(
            mapped.get("metadata", {}),
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        ),
    )
