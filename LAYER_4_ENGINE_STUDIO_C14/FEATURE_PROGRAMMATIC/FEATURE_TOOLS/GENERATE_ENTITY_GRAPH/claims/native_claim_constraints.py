"""Project native declaration constraints without executing Claim code."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...ADAPTERS_C30.model.topic_dependencies__pub import (
    validate_dependencies_claim,
)
from .primitives.primitives__shared import (
    _named_property_count as _named_property_count,
)
from .primitives.primitives__shared import _record
from .helpers.helpers__shared import _native_count as _native_count
from .rules.rules__shared import (
    _native_entity as _native_entity,
    _native_entity_dependents as _native_entity_dependents,
    _native_entity_population as _native_entity_population,
)
from .rules.rules__shared import (
    _native_property as _native_property,
    _native_property_scalar as _native_property_scalar,
    _native_property_dependents as _native_property_dependents,
)
from .rules.rules__shared import (
    _native_property_rules as _native_property_rules,
    _native_property_fallbacks as _native_property_fallbacks,
)
from .rules.rules__shared import _native_relation as _native_relation

Record = dict[str, Any]


def _native_constraints(
    declaration: Mapping[str, Any], source: Mapping[str, Any], block: str
) -> list[Record]:
    args = declaration["arguments"]
    result: list[Record] = []
    check = declaration.get("instance_check")
    if check is not None:
        scope_check = (
            args.get("base_path") == "Scope Unit"
            and args.get("entity_name") == "structural_level"
            and check.get("name") == "check_structural_level"
            and check.get("parameter_type") == "ScopeUnit"
        )
        if check.get("name") == "dependencies_are_distinct":
            validate_dependencies_claim(declaration)
        elif not (
            scope_check
            and args.get("relation_name") == "IS_PROPERTY_OF"
            or args.get("entity_class") == check["parameter_type"]
        ):
            raise ValueError("unsupported instance check")
        result.append(
            _record(
                source,
                f"{check['name']}({check['parameter']}: "
                f"{check['parameter_type']})",
                "instance_check",
                group="instances",
                callback=check["name"],
            )
        )
    if declaration["kind"] == "entity" and args.get("entity_class"):
        return _native_entity(declaration, source, block, result)
    if (
        declaration["kind"] == "entity"
        and args.get("relation_name") == "IS_PROPERTY_OF"
    ):
        return _native_property(declaration, source, block, result)
    if declaration["kind"] == "relation":
        _native_relation(declaration, source, block, result)
    return result
