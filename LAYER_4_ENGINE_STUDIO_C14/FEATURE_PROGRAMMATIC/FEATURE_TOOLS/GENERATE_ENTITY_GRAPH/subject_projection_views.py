"""Pure Markdown views over ``build_subject_projection_data`` output."""

from __future__ import annotations

from collections.abc import Mapping, Sequence as Sequence
import re as re
from typing import Any

from ._subject_projection_view_helpers import (
    _cardinality as _cardinality,
    _claims as _claims,
    _contract_channels as _contract_channels,
    _declaration_claims as _declaration_claims,
    _entities as _entities,
    _entity_claims as _entity_claims,
    _fence as _fence,
    _formal_fence as _formal_fence,
    _properties as _properties,
    _render_contracts as _render_contracts,
    _render_diagnostics as _render_diagnostics,
    _render_relation_declarations as _render_relation_declarations,
)
from .subject_projection_outline import (
    _namespace_rows,
    _refs,
    _render_namespace,
    _source_ref as _source_ref,
    _tree,
)


def _render_property(
    lines: list[str], property: Mapping[str, Any], level: int
) -> None:
    identity = str(property.get("identity", "[missing Property identity]"))
    relative = str(property.get("relative_name", identity))
    tags = " ".join(
        tag
        for tag in (
            "[inherited]" if property.get("inherited") else "",
            "[overridden]" if property.get("overridden") else "",
            "[multiple applicable declarations]"
            if property.get("multiple_applicable")
            else "",
        )
        if tag
    )
    tags = f" {tags}" if tags else ""
    refs = _refs(property.get("declaration_refs"))
    for source in refs or ["missing Declaration data"]:
        lines.append(
            f"- property: `{identity}` (relative `{relative}`)"
            f"{tags} — {source}"
        )
    if property.get("inherited") and property.get("origin_entity"):
        lines.append(f"  - origin: `{property['origin_entity']}`")
    _render_property_details(lines, property, level, refs)


def _render_properties(
    lines: list[str], data: Mapping[str, Any], level: int
) -> None:
    heading = (
        "Property declarations"
        if level == 4
        else "Direct properties"
        if level == 2
        else "Effective properties"
    )
    lines.extend(["", f"## {heading}", ""])
    shown = False
    for entity in _entities(data):
        properties = _properties(entity, level)
        if not properties:
            continue
        shown = True
        lines.extend([f"### `{entity['identity']}`", ""])
        refs = _refs(entity.get("declaration_refs"))
        lines.append(
            "- Declaration sources: "
            + (
                ", ".join(refs)
                if refs
                else "[missing Current Requirement/Form Declaration]"
            )
        )
        overridden = (
            {
                old.get("identity")
                for rules in entity.get("property_rule_origins", {}).values()
                for rule in rules
                for old in rule.get("replaces", [])
            }
            if level == 4
            else set()
        )
        for property in properties:
            if property.get("identity") in overridden:
                property = {**property, "overridden": True}
            _render_property(lines, property, level)
        lines.append("")
    if not shown:
        lines.append("- None supplied.")


def _render_primary_claims(lines: list[str], data: Mapping[str, Any]) -> None:
    entities = _entities(data)
    by_identity = {str(entity["identity"]): entity for entity in entities}
    lines.extend(["", "## Primary Declaration Formal Claims", ""])
    for entity in entities:
        identity = str(entity["identity"])
        lines.extend([f"### `{identity}`", ""])
        declaration_refs = _refs(entity.get("declaration_refs"))
        own = _entity_claims(data, entity)
        if own:
            lines.append("- own Declaration:")
            for source, block, label in own:
                lines.append(f"  - source: `{source or 'missing source'}`")
                lines.extend(_formal_fence(block, label).splitlines())
        else:
            lines.append(
                "- own Declaration: [missing Formal Claim block]"
                if declaration_refs
                else (
                    "- own Declaration: [missing Current "
                    "Requirement/Form Declaration]"
                )
            )
        for ancestor in entity.get("ancestors", []):
            ancestor = str(ancestor)
            parent = by_identity.get(ancestor)
            claims = (
                _entity_claims(data, parent)
                if parent
                else _declaration_claims(data, ancestor)
            )
            refs = _refs(parent.get("declaration_refs")) if parent else []
            lines.append(f"- ancestor Declaration `{ancestor}`:")
            if claims:
                for source, block, label in claims:
                    lines.append(f"  - source: `{source or 'missing source'}`")
                    lines.extend(_formal_fence(block, label).splitlines())
            else:
                lines.append(
                    "  - [missing Formal Claim block]"
                    if refs
                    else "  - [missing Current Requirement/Form Declaration]"
                )
        lines.append("")


def _render_rule_origins(lines: list[str], data: Mapping[str, Any]) -> None:
    lines.extend(["", "## Entity rule origins", ""])
    for entity in _entities(data):
        properties = entity.get("property_rule_origins", {})
        relations = entity.get("relation_rule_origins", {})
        if not any(properties.values()) and not any(relations.values()):
            continue
        lines.extend([f"### `{entity['identity']}`", ""])
        for group, label in (
            ("declared_here", "Declared here"),
            ("inherited", "Inherited"),
            ("overridden_here", "Overridden here"),
        ):
            property_rows = properties.get(group, [])
            relation_rows = relations.get(group, [])
            if not property_rows and not relation_rows:
                continue
            lines.extend([f"#### {label}", ""])
            for row in property_rows:
                refs = (
                    ", ".join(_refs(row.get("declaration_refs")))
                    or "missing Declaration data"
                )
                lines.append(f"- Property `{row['identity']}` — {refs}")
                for old in row.get("replaces", []):
                    old_refs = (
                        ", ".join(_refs(old.get("declaration_refs")))
                        or "missing Declaration data"
                    )
                    lines.append(
                        f"  - Replaces rule from "
                        f"`{old['origin_entity']}` — {old_refs}"
                    )
                    _render_contracts(
                        lines, old, _refs(old.get("declaration_refs"))
                    )
            _render_relation_origins(lines, entity, relation_rows)
            lines.append("")


def _render_relation_origins(lines, entity, relation_rows):
    for row in relation_rows:
        refs = (
            ", ".join(_refs(row.get("declaration_refs")))
            or "missing Declaration data"
        )
        derivation = row.get("derivation") or "unclassified"
        lines.append(
            f"- Relation `{row['relation']}` ({derivation}, "
            f"{row['level']}, {row['direction']}) — {refs}"
        )
        if row.get("expression") and "\n" not in row["expression"]:
            lines.append(f"  - Rule: `{row['expression']}`")
        elif row.get("contract"):
            lines.append(f"  - Contract: `{row['contract']}`")
        if row["origin_entity"] != entity["identity"]:
            lines.append(f"  - Origin: `{row['origin_entity']}`")
        for old in row.get("replaces", []):
            old_refs = (
                ", ".join(_refs(old.get("declaration_refs")))
                or "missing Declaration data"
            )
            lines.append(
                f"  - Replaces rule from `{old['origin_entity']}` — {old_refs}"
            )
            contract = old.get("contract")
            if isinstance(contract, Mapping):
                expression = contract.get("expression")
                if isinstance(expression, str) and "\n" not in expression:
                    lines.append(f"    - Rule: `{expression}`")
                else:
                    lines.append(f"    - Contract: `{contract}`")


def render_primary_projection(data: Mapping[str, Any], level: int) -> str:
    """Render one of the first four primary Subject views as Markdown body."""

    if type(level) is not int or level not in {1, 2, 3, 4}:
        raise ValueError("Primary projection level must be 1, 2, 3, or 4")
    tree_lines = _tree(data)
    lines = [
        "## Primary entities",
        "",
        "NARROWER_THAN: `/`",
        "",
        *_fence(tree_lines),
        "",
    ]
    lines.extend(_render_namespace(_namespace_rows(data)))
    if level >= 2:
        _render_properties(lines, data, level)
    if level == 4:
        _render_primary_claims(lines, data)
        _render_rule_origins(lines, data)
        _render_relation_declarations(lines, data)
    _render_diagnostics(lines, data)
    return "\n".join(lines).rstrip() + "\n"


__all__ = ["render_primary_projection"]


def _render_property_details(lines, property, level, refs):
    if level >= 3:
        _render_contracts(lines, property, refs)
        if "effective_value_format" in property:
            sources = [
                ref
                for source in property.get(
                    "effective_value_format_sources", []
                )
                for ref in _refs(source)
            ]
            lines.append(
                f"  - effective value format: "
                f"`{property['effective_value_format']}` — "
                f"{', '.join(sources) or 'missing source'}"
            )
        for clause in property.get("instance_constraints", []):
            if isinstance(clause, Mapping):
                each_schema = "each Property schema per bearer"
                scope = {
                    "per_bearer_each_schema": each_schema,
                    "project": "project population",
                }.get(clause.get("scope"))
                expression = clause.get("expression", "")
                source_refs = ", ".join(_refs(clause.get("source")))
                lines.append(
                    f"  - instance constraint: `{expression}` — "
                    f"{source_refs or 'missing source'}"
                    + (f"; scope: {scope}" if scope else "")
                )
    if level == 4:
        claims = _claims(property.get("formal_claims"))
        if claims:
            lines.append("  - Property Declaration Formal Claim:")
            for source, block, label in claims:
                lines.append(f"    - source: `{source or 'missing source'}`")
                lines.extend(_formal_fence(block, label).splitlines())
        else:
            lines.append(
                "  - Property Declaration Formal Claim: "
                "[missing Formal Claim block]"
            )
