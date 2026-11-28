"""Match Subject occurrences to admitted declarations and definitions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Path as _subject_Path,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    matches_named_value as matches_named_value,
)
from ._subject_audit_targets import (
    defaultdict as defaultdict,
    _authored_subjects as _authored_subjects,
    _canonical as _canonical,
    _source as _source,
    _entity_definitions as _entity_definitions,
    _entity_target as _entity_target,
    _local_target as _local_target,
    _property_parts as _property_parts,
    _term_definitions as _term_definitions,
    _term_identity as _term_identity,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contracts.contracts__shared import (
    _target as _contract_target,  # noqa: F401
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subjects.subjects__shared import (
    _has_selection,  # noqa: F401
    _model_target,  # noqa: F401
    _target_kind,  # noqa: F401
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declarations.declarations__shared import (
    _view,  # noqa: F401
)
from ...contracts.contracts__shared import (
    _conditional_target,
)
from ...subjects.subjects__shared import (
    namespace_local_expression,
)
from ...declarations.declarations__shared import (
    Record,
)
from .subject_audit_occurrences import (
    _pin,
)


def _declaration_catalog(
    data: Mapping[str, Any],
) -> dict[tuple[str, str], list[Record]]:
    declarations = data["declarations"]
    catalog = {
        ("primary_node", identity): rows
        for identity, rows in declarations.get("primary_nodes", {}).items()
    }
    for kind_name, key in (
        ("property", "properties"),
        ("instance", "instances"),
        ("relation", "relations"),
        ("component", "components"),
    ):
        catalog.update(
            {
                (kind_name, identity): rows
                for identity, rows in declarations.get(key, {}).items()
            }
        )
    return catalog


def _conditional_coverage(
    subject: str, catalog: Mapping[tuple[str, str], list[Record]]
) -> Record | None:
    expression = _subject_parse_subject_expression(
        subject, subject_profile="approved"
    ).expression
    expression = namespace_local_expression(expression) or expression
    conditional = _conditional_target(expression, catalog)
    if conditional is None:
        return None
    bound, binding, _ = conditional
    return {
        "status": "covered",
        "base_target": bound[1],
        "binding": binding,
        "declaration_refs": [_pin(row["source"]) for row in catalog[bound]],
    }


def _inherited_property_coverage(
    identity: str, data: Mapping[str, Any]
) -> Record | None:
    parts = _property_parts(identity)
    if parts is None:
        return None
    origin, relative = parts
    entity = next(
        (row for row in data["entities"] if row["identity"] == origin), None
    )
    if entity is None:
        return None
    inherited = [
        row
        for row in entity["inherited_properties"]
        if row["relative_name"] == relative
    ]
    if not inherited:
        return None
    return {
        "status": "covered",
        "target": identity,
        "inherited": True,
        "declaration_refs": sorted(
            {ref for row in inherited for ref in row["declaration_refs"]}
        ),
    }


def _instance_coverage(
    identity: str, declarations: Mapping[str, Any]
) -> Record | None:
    expression = _subject_parse_subject_expression(
        identity, subject_profile="approved"
    ).expression
    assert isinstance(expression, _subject_Path)
    index = next(
        (
            i
            for i, step in enumerate(expression.steps)
            if step.operator == "//"
        ),
        None,
    )
    if index is not None:
        base = _subject_render_subject(
            replace(
                expression,
                steps=expression.steps[:index],
                value_format=None,
                value_cardinality=None,
            )
        )
        declared = declarations["primary_nodes"].get(base)
        if declared:
            return {
                "status": "covered",
                "target": identity,
                "base_target": base,
                "declaration_refs": [_pin(row["source"]) for row in declared],
            }
    return None


def _coverage(
    subject: str,
    data: Mapping[str, Any],
    definitions: Mapping[str, list[Record]],
    term_definitions: Mapping[str, list[Record]],
) -> Record:
    declarations = data["declarations"]
    known = _declaration_catalog(data)
    target = _local_target(subject)
    if target is None:
        conditional = _conditional_coverage(subject, known)
        return (
            {**conditional, "target": conditional["base_target"]}
            if conditional is not None
            else {
                "status": "unresolved",
                "message": (
                    "Subject is not one direct known target; review required."
                ),
            }
        )
    kind, identity = target
    direct = _direct_coverage(kind, identity, declarations)
    if direct is not None:
        return direct
    if kind == "property":
        inherited = _inherited_property_coverage(identity, data)
        if inherited is not None:
            return inherited
    if kind == "instance":
        inherited = _instance_coverage(identity, declarations)
        if inherited is not None:
            return inherited
    conditional = _conditional_coverage(subject, known)
    if conditional is not None:
        return {**conditional, "target": identity}
    return _fallback_coverage(
        subject, kind, identity, definitions, term_definitions
    )


def _direct_coverage(kind, identity, declarations):
    catalog = {
        "primary_node": "primary_nodes",
        "property": "properties",
        "instance": "instances",
        "relation": "relations",
        "component": "components",
    }.get(kind)
    keys = (
        [identity, identity.removeprefix("Relation//")]
        if kind == "relation"
        else [identity]
    )
    direct = next(
        (
            declarations.get(catalog, {}).get(key)
            for key in keys
            if declarations.get(catalog, {}).get(key)
        ),
        None,
    )
    if direct:
        return {
            "status": "covered",
            "target": identity,
            "declaration_refs": [_pin(row["source"]) for row in direct],
        }
    return None


def _fallback_coverage(subject, kind, identity, definitions, term_definitions):
    term_identity = _term_identity(subject)
    if term_identity is not None and term_identity in term_definitions:
        return {
            "status": "outside_required_scope",
            "target": identity,
            "message": (
                "Term has a Method / Term Definition; "
                "outside Requirement Declaration scope"
            ),
            "term_definition_refs": [
                _pin(source) for source in term_definitions[term_identity]
            ],
        }
    definition_refs = definitions.get(subject, [])
    if kind == "component" and definition_refs:
        return {
            "status": "outside_required_scope",
            "target": identity,
            "message": (
                "no Requirement Declaration; existing Entity Definition; "
                "outside R2469 required scope"
            ),
            "entity_definition_refs": [
                _pin(source) for source in definition_refs
            ],
        }
    return {
        "status": "missing",
        "target": identity,
        "message": (
            "No effective Requirement / Declaration coverage "
            "in the selected sources."
        ),
    }
