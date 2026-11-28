"""Resolve relation targets and materialized value fields."""

from collections.abc import Mapping
import datetime as dt
import sys
from typing import Any
from ...relation_registry import RelationRegistry
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    carriers.content.content__shared import (
        carrier_read_view,
        is_logical_container,
    )  # fmt: skip

ATOM = "Atom"
SCOPE = "Scope Unit"


def _relation_name(
    value: str,
    registry: RelationRegistry,
    source_path: str | None = None,
) -> tuple[str, bool] | None:
    addresses = (
        {name: (name, False) for name in registry.names}
        | {
            inverse: (direct, True)
            for direct, inverse in registry.inverse.items()
        }
        | {alias: (name, True) for alias, name in registry.aliases.items()}
    )
    if value in addresses:
        return addresses[value]
    matches = sorted(
        name for name in addresses if name.casefold() == value.casefold()
    )
    if len(matches) == 1:
        return addresses[matches[0]]
    if matches and source_path is not None:
        print(
            f"Workbench: {source_path}: ambiguous registered Relation {value}"
            "; "
            f"candidates: {', '.join(matches)}; link skipped",
            file=sys.stderr,
        )
    return None


def _targets(
    value: Any, scope_references: Mapping[str, str], kind: str | None = None
):
    if isinstance(value, str):
        if kind == SCOPE:
            yield SCOPE, scope_references.get(value, value)
        elif kind == ATOM:
            yield ATOM, value
        elif value in scope_references:
            yield SCOPE, scope_references[value]
        else:
            yield ATOM, value
    elif isinstance(value, list):
        for item in value:
            yield from _targets(item, scope_references, kind)
    elif isinstance(value, dict):
        for key, target_kind in (("atom", ATOM), ("scope_unit", SCOPE)):
            if key in value:
                yield from _targets(value[key], scope_references, target_kind)


def _scope_references(scopes: list[dict]) -> dict[str, str]:
    return {
        reference: row["name"]
        for row in scopes
        for reference in (row["name"], row["scope_unit_id"])
        if isinstance(reference, str) and reference
    }


def _container(
    row: Mapping[str, Any],
    scope_references: Mapping[str, str],
) -> tuple[str | None, str | None]:
    root_header = row.get("_project_root_header")
    container = carrier_read_view(
        dict(row["header_json"] if root_header is None else root_header)
    ).get("container")
    if root_header is not None and not is_logical_container(container):
        return None, None
    if isinstance(container, Mapping):
        scope = container.get("scope_unit")
        if isinstance(scope, str):
            return SCOPE, scope_references.get(scope, scope)
        atom = container.get("atom")
        if isinstance(atom, str):
            return ATOM, atom
    legacy = row.get("current_scope_unit")
    return (
        (SCOPE, scope_references.get(legacy, legacy))
        if isinstance(legacy, str)
        else (None, None)
    )


def _edge(fact, derived: bool) -> dict[str, Any]:
    source_kind, source_ref, relation, target_kind, target_ref = fact
    return {
        "source_kind": source_kind,
        "source_ref": source_ref,
        "target_kind": target_kind,
        "target_ref": target_ref,
        "relation_type": relation,
        "derived": derived,
    }


def _timestamp(value: Any) -> str | None:
    try:
        timestamp = (
            value
            if isinstance(value, dt.datetime)
            else dt.datetime.fromisoformat(value)
        )
    except TypeError, ValueError:
        return None
    return (
        timestamp.astimezone(dt.timezone.utc).isoformat()
        if timestamp.tzinfo
        else None
    )
