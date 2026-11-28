"""Entity definition and active Subject summary."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    SubjectNotationError as _subject_SubjectNotationError,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    matches_named_value,
)
from ...declarations.declarations__shared import Record, _view
from .subject_audit_coverage import (
    _entity_target,
    _property_parts,
    _term_identity,
)
from .subject_audit_occurrences import _pin, _source


def _is_defining(carrier: Mapping[str, Any], target: tuple[str, str]) -> bool:
    source = _source(carrier)
    atom_id = str(source.get("atom_id", ""))
    form = str(_view(carrier).get("type", ""))
    if atom_id.startswith("CA-R-") and (
        form.endswith("Declaration") or form.endswith("Definition")
    ):
        return True
    return (
        atom_id.startswith("CA-M-")
        and matches_named_value(_view(carrier).get("content_role"), "Method")
        and matches_named_value(form, "Term Definition")
        and target[0] == "component"
        and _term_identity(target[1]) is not None
    )


def _inherited_definition_refs(
    target: tuple[str, str], data: Mapping[str, Any]
) -> list[str]:
    if target[0] != "property":
        return []
    parts = _property_parts(target[1])
    if parts is None:
        return []
    origin, relative = parts
    entity = next(
        (row for row in data["entities"] if row["identity"] == origin), None
    )
    if entity is None:
        return []
    return sorted(
        {
            ref
            for row in entity["inherited_properties"]
            if row["relative_name"] == relative
            for ref in row["declaration_refs"]
        }
    )


def _entity_summary(
    carriers: list[Record], occurrences: list[Record], data: Mapping[str, Any]
) -> Record:
    """Separate defining-carrier coverage from active Subject coverage."""

    rows = _entity_occurrence_rows(carriers, occurrences, data)
    entities = _summary_entities(rows)
    return {
        "kind": "entity_definition_summary",
        "entities": entities,
        "display_entities": [
            row
            for row in entities
            if row["missing_definition"] or row["missing_active"]
        ],
        "coverage": {
            "entities": len(entities),
            "entities_with_any_missing": sum(
                row["missing_definition"] or row["missing_active"]
                for row in entities
            ),
        },
    }


def _summary_entities(rows):
    entities = []
    for row in rows.values():
        defining_refs, active_refs = (
            sorted(row["defining_refs"]),
            sorted(row["active_refs"]),
        )
        entities.append(
            {
                **row,
                "defining_refs": defining_refs,
                "active_refs": active_refs,
                "missing_definition": not defining_refs,
                "missing_active": not active_refs,
                "subjects": sorted(
                    row["subjects"],
                    key=lambda item: (
                        item["pin"],
                        item["source_key"],
                        item["raw_value"],
                    ),
                ),
            }
        )
    entities.sort(key=lambda row: (row["kind"], row["identity"]))
    return entities


def _entity_occurrence_rows(carriers, occurrences, data):
    source_index = {
        (
            str(_source(carrier).get("path", "")),
            _pin(_source(carrier)),
        ): carrier
        for carrier in carriers
    }
    rows: dict[tuple[str, str], Record] = {}
    for occurrence in occurrences:
        if occurrence["subject"] is None:
            continue
        try:
            target = _entity_target(occurrence["subject"])
        except _subject_SubjectNotationError:
            target = None
        if target is None:
            continue
        row = rows.setdefault(
            target,
            {
                "identity": target[1],
                "kind": target[0],
                "defining_refs": set(),
                "active_refs": set(),
                "subjects": [],
            },
        )
        row["subjects"].append(
            {
                key: occurrence[key]
                for key in ("raw_value", "pin", "source_key", "role", "source")
            }
        )
        row["defining_refs"].update(_inherited_definition_refs(target, data))
        carrier = source_index.get(
            (str(occurrence["source"].get("path", "")), occurrence["pin"])
        )
        if occurrence["role"] == "active":
            row["active_refs"].add(occurrence["pin"])
            if carrier is not None and _is_defining(carrier, target):
                row["defining_refs"].add(occurrence["pin"])
    return rows
