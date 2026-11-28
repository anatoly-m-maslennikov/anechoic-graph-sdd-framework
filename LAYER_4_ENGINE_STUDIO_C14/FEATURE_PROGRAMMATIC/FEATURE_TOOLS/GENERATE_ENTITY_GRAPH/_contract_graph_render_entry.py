"""Render source-bound contract entry details."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from .contracts.contracts__shared import _source_ref

Record = dict[str, Any]


def _count(value: object) -> str:
    if not isinstance(value, Mapping):
        return "undefined"
    lower, upper = value.get("minimum"), value.get("maximum")
    return (
        f"{lower}+"
        if upper is None
        else str(lower)
        if lower == upper
        else f"{lower}..{upper}"
    )


def _relation_clause(row):
    relation = (
        row.get("relation") or row.get("relation_notation") or "relation"
    )
    written = row.get("written_direction", "forward")
    if row.get("target_selector") is None:
        return (
            f"`{row.get('source_selector')}` — {relation}; outgoing "
            f"count={_count(row.get('source_cardinality'))}; "
            "target domain unresolved from "
            f"this clause; written direction={written}"
        )
    return (
        f"`{row.get('source_selector')}` — {relation} → "
        f"`{row.get('target_selector')}`; "
        f"Host={_count(row.get('source_cardinality'))}; "
        f"Target={_count(row.get('target_cardinality'))}; "
        f"written direction={written}"
    )


def _property_clause(row):
    effective = (
        "conflict"
        if row.get("occurrence_conflict")
        else _count(row.get("effective_occurrence_cardinality"))
    )
    written = (
        _count(row["occurrence_cardinality"])
        if row.get("occurrence_cardinality") is not None
        else "omitted"
    )
    return (
        f"`{row.get('property_selector')}` {row.get('selection')}; "
        f"names={row.get('name_format')}; "
        f"written names count={written}; effective "
        f"names count={effective}; "
        f"values={row.get('value_format')}; values "
        f"count={_count(row.get('value_cardinality'))}"
    )


def _clause(row: Mapping[str, Any]) -> str:
    if row.get("kind") == "relation_endpoint_pair":
        targets = (
            _count(row["targets_per_source"])
            if row.get("targets_per_source") is not None
            else "omitted"
        )
        sources = (
            _count(row["sources_per_target"])
            if row.get("sources_per_target") is not None
            else "omitted"
        )
        return (
            f"Host={row['source_endpoint']}; Target={row['target_endpoint']}; "
            f"targets per source={targets}; sources per target={sources}"
        )
    if row.get("kind") == "relation_cardinality":
        return _relation_clause(row)
    if row.get("kind") == "property_constraint":
        return _property_clause(row)
    if row.get("kind") == "effective_value_fallback_chain":
        lookup, project = row["branches"]
        return (
            f"`{row['property_selector']}` when undefined, null, or empty: "
            f"nearest `{lookup['lookup_property']}` "
            f"via `{lookup['lookup_relation']}`, then "
            f"`{project['project_property']}` "
            f"from one `{project['project_entity']}`"
        )
    return _other_clause(row)


def _other_clause(row: Mapping[str, Any]) -> str:
    if row.get("kind") == "population_unique_constraint":
        text = (
            f"`{row['population_selector']}`: unique {', '.join(row['keys'])}"
        )
        if "status" in row:
            text += (
                f" for {row['status']} states with one value for "
                f"{', '.join(row['single_value_paths'])}"
            )
        return text
    if row.get("kind") == "population_functional_dependency":
        groups = (
            f"; Status Group in ({', '.join(row['status_groups'])})"
            if "status_groups" in row
            else ""
        )
        return (
            f"`{row['population_selector']}`: {', '.join(row['keys'])} "
            f"determines {', '.join(row['dependents'])}{groups}"
        )
    if row.get("kind") == "native_population_constraint":
        return (
            f"Population count={_count(row.get('cardinality'))}; "
            f"scope={row.get('scope')}"
        )
    if row.get("kind") == "native_class":
        return (
            f"Class {row.get('class_name')} inherits "
            f"{', '.join(row.get('bases', ()))}"
        )
    if row.get("kind") == "allowed_literal":
        return f"`{row.get('property_selector')}: {row.get('literal')}`"
    if row.get("kind") == "axis_allowed_value":
        return (
            f"`{row.get('subject_selector')} >| {row.get('axis')}: "
            f"{row.get('value')}`"
        )
    if row.get("kind") == "axis_condition":
        return (
            f"`{row.get('subject_selector')} >| {row.get('axis')} "
            f"{row.get('operator')} {row.get('value')}`"
        )
    return f"`{row.get('expression')}`"


def _fence(block: Mapping[str, Any]) -> list[str]:
    if str(block.get("label", "")).casefold() == "python":
        content = str(block["block"])
        marker = "`" * max(
            [3] + [len(value) + 1 for value in re.findall(r"`+", content)]
        )
        rows = content.split("\n")
        if rows[-1] == "":
            rows.pop()
        return [marker + str(block["label"]), *rows, marker]
    content = str(block["block"]).rstrip()
    marker = "`" * max(
        [3] + [len(value) + 1 for value in re.findall(r"`+", content)]
    )
    label = str(block.get("label", ""))
    status = "" if block.get("closed", True) else " (unclosed in source)"
    return [marker + label, content, marker + status]


def _clause_group(clause: Mapping[str, Any]) -> str:
    if clause.get("kind") == "property_constraint":
        return (
            "Value contracts"
            if clause.get("selection") == "values"
            else "Nested Property contracts"
        )
    if clause.get("kind") == "allowed_literal":
        return "Allowed values"
    return "Allowed Relations and other formal clauses"


def _render_clause_groups(lines: list[str], clauses: list[Record]) -> None:
    groups: dict[str, list[str]] = {
        "Value contracts": [],
        "Nested Property contracts": [],
        "Allowed values": [],
        "Allowed Relations and other formal clauses": [],
    }
    for clause in clauses:
        title = _clause_group(clause)
        groups[title].append(_clause(clause))
    for title, values in groups.items():
        if values:
            lines.extend(
                [f"  - {title}:", *["    - " + value for value in values]]
            )


def _render_entry_tail(lines, entry):
    for diagnostic in entry["diagnostics"]:
        lines.append(
            f"  - Unresolved Python Formal Claim: "
            f"`{diagnostic.get('expression', diagnostic.get('message'))}`"
        )
    if entry["semantics"]:
        lines.extend(
            [
                "  - Semantics:",
                *[
                    "    " + row if row else ""
                    for row in entry["semantics"].splitlines()
                ],
            ]
        )
    if entry["details"]:
        lines.extend(
            [
                "  - Details (source-bound):",
                *[
                    "    " + row if row else ""
                    for row in entry["details"].splitlines()
                ],
            ]
        )


def _render_entry(lines: list[str], entry: Record, label: str) -> None:
    lines.append(f"- {label}: `{_source_ref(entry['source'])}`")
    if entry["claim_scope"]:
        lines.extend(
            [
                "  - Claim Scope:",
                *[
                    "    " + row if row else ""
                    for row in entry["claim_scope"].splitlines()
                ],
            ]
        )
    if entry["prose"]:
        lines.extend(
            [
                "  - Remaining Claim prose:",
                *[
                    "    " + row if row else ""
                    for row in entry["prose"].splitlines()
                ],
            ]
        )
    for block in entry["blocks"]:
        lines.extend(["  - Fenced Claim block:", *_fence(block)])
    _render_clause_groups(lines, entry["clauses"])
    if entry["instance_clauses"]:
        lines.extend(
            [
                "  - Instance constraints:",
                *[
                    "    - " + _clause(row)
                    for row in entry["instance_clauses"]
                ],
            ]
        )
    _render_entry_tail(lines, entry)


def _render_contract_rows(lines: list[str], row: Record) -> None:
    for own in row["own"]:
        _render_entry(lines, own, "Declaration source")
    for shared in row["shared"]:
        binding = shared.get("binding", "exact")
        _render_entry(lines, shared, f"Shared RMED source ({binding} binding)")
        if shared.get("binding_context"):
            lines.extend(
                [
                    "  - Binding context:",
                    *[
                        f"    - {key.replace('_', ' ')}: `{value}`"
                        for key, value in shared["binding_context"].items()
                    ],
                ]
            )
