"""Exact carrier evidence shared by declaration readers."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
from pathlib import Path
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import source_body
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import SubjectNotationError, parse_subject_expression


Record = dict[str, Any]


def _view(carrier: Mapping[str, object]) -> Mapping[str, object]:
    """Use migrated Role/Form and Subject aliases without changing evidence."""

    value = carrier.get("read_view")
    if isinstance(value, Mapping):
        return value
    metadata = carrier.get("metadata")
    return carrier_read_view(dict(metadata)) if isinstance(metadata, Mapping) else {}


def _source(carrier: Mapping[str, object]) -> Record | None:
    value = carrier.get("source")
    if not isinstance(value, Mapping):
        return None
    atom_id, version = value.get("atom_id"), value.get("version")
    if not isinstance(atom_id, str) or not atom_id.strip() or type(version) is not int or version < 1:
        return None
    return {key: item for key, item in value.items()}


def _source_with_matching_bytes(
    source: Record | None, raw: object, raw_body: object
) -> Record | None:
    if source is None or not isinstance(raw, bytes) or not isinstance(raw_body, str):
        return None
    if hashlib.sha256(raw).hexdigest() != source.get("sha256"):
        return None
    try:
        raw.decode("utf-8")
        path = Path(str(source.get("path", "supplied.md")))
        exact_body = source_body(raw, path).decode("utf-8")
    except ValueError:
        return None
    if raw_body != exact_body:
        return None
    return source


def _subjects(carrier: Mapping[str, object]) -> list[str]:
    subjects = _subjects_mapping(carrier)
    if not isinstance(subjects, Mapping):
        return []
    value = subjects.get("governs")
    values = value if isinstance(value, list) else [value]
    return [item for item in values if isinstance(item, str) and item.strip()]


def _single_valid_governed_subject(carrier: Mapping[str, object]) -> str | None:
    subjects = _subjects_mapping(carrier)
    if not isinstance(subjects, Mapping):
        return None
    value = subjects.get("governs")
    values = value if isinstance(value, list) else [value]
    if len(values) != 1 or not isinstance(values[0], str) or not values[0].strip():
        return None
    try:
        parse_subject_expression(values[0], subject_profile="approved")
    except SubjectNotationError:
        return None
    return values[0]


def _subjects_mapping(carrier: Mapping[str, object]) -> Mapping[str, object] | None:
    subjects = carrier.get("subjects")
    if not isinstance(subjects, Mapping):
        subjects = _view(carrier).get("subjects")
    if not isinstance(subjects, Mapping):
        return None
    return carrier_read_view({"subjects": dict(subjects)}).get("subjects")


def _active_source_matches_metadata(
    source: Record | None, metadata: Mapping[str, object]
) -> bool:
    return bool(
        source is not None
        and metadata.get("atom_id") == source.get("atom_id")
        and type(metadata.get("version")) is int
        and metadata.get("version") == source.get("version")
        and metadata.get("status") in {"Active", "active"}
    )
