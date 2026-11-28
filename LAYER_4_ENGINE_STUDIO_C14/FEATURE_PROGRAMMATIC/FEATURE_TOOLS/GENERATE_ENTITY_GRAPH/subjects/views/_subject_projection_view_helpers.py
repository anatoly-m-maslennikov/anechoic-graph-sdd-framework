"""Shared rendering helpers for Subject projections."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import re
from typing import Any

from .subject_projection_outline import _refs, _source_ref


def _claims(value: object) -> list[tuple[str | None, str, str]]:
    if not isinstance(value, Sequence) or isinstance(
        value, (str, bytes, bytearray)
    ):
        return []
    return [
        (
            _source_ref(row.get("source")),
            row["block"],
            row.get("label", "python"),
        )
        for row in value
        if isinstance(row, Mapping) and isinstance(row.get("block"), str)
    ]


def _fence(lines: Sequence[str], label: str = "text") -> list[str]:
    width = max(
        [3]
        + [
            len(match.group(0)) + 1
            for line in lines
            for match in re.finditer(r"`+", line)
        ]
    )
    marker = "`" * width
    return [f"{marker}{label}", *lines, marker]


def _formal_fence(block: str, label: str) -> str:
    width = max(
        [3] + [len(match.group(0)) + 1 for match in re.finditer(r"`+", block)]
    )
    marker = "`" * width
    content = block if block.endswith("\n") else block + "\n"
    return f"{marker}{label}\n{content}{marker}"


def _entities(data: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [row for row in data["entities"] if isinstance(row, Mapping)]


def _declaration_claims(
    data: Mapping[str, Any], identity: str
) -> list[tuple[str | None, str, str]]:
    entries = (
        data.get("declarations", {}).get("primary_nodes", {}).get(identity, [])
    )
    return [
        claim
        for entry in entries
        for claim in _claims(entry.get("python_blocks", []))
    ]


def _entity_claims(
    data: Mapping[str, Any], entity: Mapping[str, Any]
) -> list[tuple[str | None, str, str]]:
    return _claims(entity.get("formal_claims")) or _declaration_claims(
        data, str(entity["identity"])
    )


def _properties(
    entity: Mapping[str, Any], level: int
) -> list[Mapping[str, Any]]:
    direct = entity.get("direct_properties", [])
    if level == 2:
        return [row for row in direct if isinstance(row, Mapping)]
    inherited = entity.get("inherited_properties", [])
    return [row for row in (*direct, *inherited) if isinstance(row, Mapping)]


def _cardinality(value: object) -> str:
    if not isinstance(value, Mapping):
        return "missing"
    minimum, maximum = value.get("minimum"), value.get("maximum")
    return (
        f"{minimum}+"
        if maximum is None
        else str(minimum)
        if maximum == minimum
        else f"{minimum}..{maximum}"
    )


def _contract_channels(contract: Mapping[str, Any]) -> list[str]:
    if contract.get("kind") == "allowed_literal":
        return [f"    - allowed literal: `{contract.get('literal', '')}`"]
    if contract.get("kind") != "property_constraint":
        return []
    channels = []
    for key, label in (
        ("selection", "nesting"),
        ("name_format", "name format"),
        ("occurrence_cardinality", "occurrence cardinality"),
        (
            "effective_occurrence_cardinality",
            "effective occurrence cardinality",
        ),
        ("value_format", "value format"),
        ("value_cardinality", "value cardinality"),
    ):
        if key in contract:
            value = (
                "omitted"
                if key == "occurrence_cardinality" and contract[key] is None
                else "conflict"
                if key == "effective_occurrence_cardinality"
                and contract.get("occurrence_conflict")
                else _cardinality(contract[key])
                if key.endswith("cardinality")
                else contract[key]
            )
            channels.append(f"    - {label}: `{value}`")
    return channels


def _render_contracts(
    lines: list[str], property: Mapping[str, Any], refs: list[str]
) -> None:
    for contract in property.get("contracts", []):
        if not isinstance(contract, Mapping):
            continue
        expression = contract.get(
            "expression", "[unwritten contract expression]"
        )
        sources = _refs(contract.get("source")) or ["missing source"]
        for source in sources:
            lines.append(f"  - contract: `{expression}` — {source}")
            lines.extend(_contract_channels(contract))


def _render_relation_declarations(
    lines: list[str], data: Mapping[str, Any]
) -> None:
    relations = data.get("relation_declarations", [])
    if not relations:
        return
    lines.extend(["", "## Relation declarations", ""])
    for classification in ("Direct", "Derived", None):
        group = [
            row for row in relations if row.get("derivation") == classification
        ]
        if not group:
            continue
        lines.extend([f"### {classification or 'Unclassified'}", ""])
        for row in group:
            refs = (
                ", ".join(_refs(row.get("declaration_refs")))
                or "missing Declaration data"
            )
            direct = ", ".join(
                f"`{name}`" for name in row.get("direct_relations", [])
            )
            lines.append(
                f"- `{row['name']}` — {refs}"
                + (f"; inverse of {direct}" if direct else "")
            )
        lines.append("")


def _render_diagnostics(lines: list[str], data: Mapping[str, Any]) -> None:
    values = [
        *data.get("diagnostics", []),
        *data["tree"].get("diagnostics", []),
    ]
    if not values:
        return
    rendered = []
    for value in values:
        if isinstance(value, Mapping):
            message = value.get(
                "expression", value.get("message", value.get("code"))
            )
            source = _source_ref(value.get("source"))
            if message is not None:
                rendered.append(
                    f"{message}" + (f" — {source}" if source else "")
                )
        else:
            rendered.append(str(value))
    if rendered:
        lines.extend(
            ["", "## Diagnostics", "", *(f"- {item}" for item in rendered)]
        )
