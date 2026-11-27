"""Render source-bound formal contract graphs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import re as re

from .contract_graph_common import (
    _source_ref,
)
from .readable_entity_tree_data import (
    primary_tree,
    read_edges,
    read_nodes,
)

from ._contract_graph_render_entry import (
    _count as _count,
    _clause as _clause,
    _other_clause as _other_clause,
    _fence as _fence,
    _clause_group as _clause_group,
    _render_clause_groups as _render_clause_groups,
    _render_entry as _render_entry,
    _render_contract_rows as _render_contract_rows,
)


_NO_DECLARATION = "no direct declaration source in selection"
_NO_KIND_SOURCE = "no declared Kind source in selection"

Record = dict[str, Any]


def _tree_lines(narrowing: Mapping[str, Any]) -> list[str]:
    nodes = read_nodes(narrowing["nodes"])
    children, _, _, _ = read_edges(narrowing["edges"], nodes)
    lines, _, _ = primary_tree(nodes, children, set(nodes))
    return [
        "## Declared Narrowing Tree",
        "",
        "Each identity has its source-bound contract below.",
        "",
        "```text",
        *lines,
        "```",
        "",
    ]


def render_contract_graph(graph: Mapping[str, Any]) -> str:
    (
        """Render complete source-bound Claims and bounded structured """
        """contract views."""
    )

    lines = [
        "# Formal Contract Graph",
        "",
        "Source-bound extraction of Python Formal Claims. Authored blocks "
        "are preserved as evidence.",
        "",
        "## Coverage",
        "",
    ]
    lines.extend(
        f"- {key.replace('_', ' ')}: {value}"
        for key, value in graph["coverage"].items()
    )
    lines.extend(
        [
            f"- display coverage: {graph['display_coverage']}",
            f"- structured Claim extraction: {graph['structured_claims']}",
        ]
    )
    lines.extend([""] + _tree_lines(graph["narrowing_tree"]))
    _render_entities(lines, graph)
    _render_relations(lines, graph)
    _render_gaps(lines, graph)
    return "\n".join(lines) + "\n"


def _declarations(row):
    return ", ".join(row["declaration_refs"]) or _NO_DECLARATION


def _kind_sources(instance_of):
    return ", ".join(instance_of["effective_source_refs"]) or _NO_KIND_SOURCE


def _render_entities(lines, graph):
    if graph.get("namespaces"):
        lines.extend(["## Namespace Declarations", ""])
        for namespace in graph["namespaces"]:
            lines.extend([f"### `{namespace['target']}` — namespace", ""])
            _render_contract_rows(lines, namespace)
            lines.append("")
    lines.extend(["## Entity and Property Contracts", ""])
    for entity in graph["entities"]:
        lines.extend([f"### `{entity['target']}` — {entity['kind']}", ""])
        if entity["kind"] == "primary_node" and entity["transitive_ancestors"]:
            lines.append(
                "- Transitive ancestor Declarations; their contracts are not "
                "copied:"
            )
            lines.extend(
                f"  - `{row['target']}` — {_declarations(row)}"
                for row in entity["transitive_ancestors"]
            )
        if entity["kind"] == "instance":
            instance_of = entity["instance_of"]
            lines.append(
                "- INSTANCE_OF declared Kind effective contracts; no "
                "instance contract is copied: "
                f"`{instance_of['target'] or 'unresolved'}` — "
                f"{_kind_sources(instance_of)}"
            )
        if entity.get("inherited_property_declarations"):
            lines.append(
                "- Inherited Property Declaration refs; no child Property "
                "Node is created:"
            )
            lines.extend(
                f"  - `{row['target']}` — {', '.join(row['declaration_refs'])}"
                for row in entity["inherited_property_declarations"]
            )
        _render_contract_rows(lines, entity)
        lines.append("")
    lines.extend(["## CFEL, Carrier, and Term Component Contracts", ""])
    for component in graph["components"]:
        lines.extend([f"### `{component['target']}` — declared component", ""])
        _render_contract_rows(lines, component)
        lines.append("")


def _render_derived_relations(lines, relation):
    if relation.get("derived_view"):
        derived = relation["derived_view"]
        lines.append(
            f"- Derived view of `{derived['direct_relation']}` — "
            f"{_source_ref(derived['source'])}; endpoints are a reversed "
            "source view, not "
            f"new permissions."
        )
        lines.extend(
            f"  - `{endpoint['host']}` → `{endpoint['target']}`"
            for endpoint in derived["endpoints"]
        )
        lines.extend(
            [
                "  - Source meaning:",
                *[
                    "    " + line if line else ""
                    for line in derived["meaning"].splitlines()
                ],
            ]
        )
    for derived in relation.get("derived_aliases", []):
        lines.append(
            f"- Derived Relation `(({derived['name']}))` — "
            f"{_source_ref(derived['source'])}; "
            "reverse view of the same Relation."
        )
        lines.extend(
            f"  - `{endpoint['host']}` → `{endpoint['target']}`; targets per "
            f"source={_count(endpoint['targets_per_source'])}; sources per "
            f"target={_count(endpoint['sources_per_target'])}"
            for endpoint in derived["endpoints"]
        )


def _render_relation_bindings(lines, relation):
    for kind in ("HAS_INVERSE", "IS_INVERSE_ALIAS_FOR"):
        bindings = [
            row
            for row in relation["inverses"]
            if row.get("relation", "HAS_INVERSE") == kind
        ]
        if bindings:
            lines.extend(
                [
                    f"- {kind} bindings; this does not certify an undeclared "
                    f"inverse Relation:",
                    *[
                        f"  - `(({row['name']}))` — "
                        f"{_source_ref(row['source'])}"
                        for row in bindings
                    ],
                ]
            )
    if relation["derivation_links"]:
        lines.extend(
            [
                "- IS_DERIVED_RELATION_OF bindings:",
                *[
                    f"  - `(({row['name']}))` — {_source_ref(row['source'])}"
                    for row in relation["derivation_links"]
                ],
            ]
        )


def _render_relations(lines, graph):
    lines.extend(["## Relation Contracts", ""])
    for relation in graph["relations"]:
        lines.extend(
            [f"### `(({relation['target']}))` — declared Relation", ""]
        )
        _render_contract_rows(lines, relation)
        if relation["host_target"]:
            lines.extend(
                [
                    "- Host / Target contracts:",
                    *[
                        "  - " + _clause(row)
                        for row in relation["host_target"]
                    ],
                ]
            )
        if relation["metadata"]:
            lines.extend(
                [
                    "- Standalone metadata:",
                    *[
                        f"  - {row['kind']}: `{row['value']}` — "
                        f"{_source_ref(row['source'])}"
                        for row in relation["metadata"]
                    ],
                ]
            )
        _render_derived_relations(lines, relation)
        if relation.get("derivation_scope"):
            lines.append(
                f"- Derivation interpretation gap: "
                f"{relation['derivation_scope']}"
            )
        _render_relation_bindings(lines, relation)
        lines.append("")


def _diagnostic_text(row):
    return row.get("expression", row.get("message"))


def _render_gaps(lines, graph):
    lines.extend(["## Coverage Gaps and Conflicts", ""])
    for row in graph["coverage_gaps"]:
        lines.append(f"- `{_source_ref(row['source'])}`: {row['message']}")
        _render_entry(lines, row, "Unbound source evidence")
    for row in graph["outside_model_scope"]:
        lines.append(f"- `{_source_ref(row['source'])}`: {row['message']}")
        _render_entry(lines, row, "Selected evidence outside model scope")
    for row in graph["conflicts"]:
        lines.append(
            f"- Duplicate {row['kind']} Declaration `{row['target']}`: "
            f"{', '.join(row['sources'])}"
        )
    for row in graph["missing_relation_semantics"]:
        lines.append(
            f"- Relation `(({row['relation']}))` lacks Semantics: "
            f"`{_source_ref(row['source'])}`"
        )
    for row in graph["instance_kind_gaps"]:
        lines.append(
            f"- Instance `{row['instance']}` has no declared Kind target: "
            f"`{row['kind'] or 'unresolved'}`"
        )
    for row in graph["diagnostics"]:
        lines.append(
            f"- `{_source_ref(row['source'])}`: {_diagnostic_text(row)}"
        )
    for message in graph["inheritance_diagnostics"]:
        lines.append(f"- Narrowing evidence: {message}")
    if not (
        graph["coverage_gaps"]
        or graph["conflicts"]
        or graph["missing_relation_semantics"]
        or graph["instance_kind_gaps"]
        or graph["diagnostics"]
        or graph["inheritance_diagnostics"]
    ):
        lines.append("- None.")
