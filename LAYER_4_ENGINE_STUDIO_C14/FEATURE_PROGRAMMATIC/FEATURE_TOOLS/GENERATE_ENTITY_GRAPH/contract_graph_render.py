"""Render source-bound formal contract graphs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import re

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_common import _source_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.readable_entity_tree_data import primary_tree, read_edges, read_nodes

Record = dict[str, Any]


def _tree_lines(narrowing: Mapping[str, Any]) -> list[str]:
    nodes = read_nodes(narrowing["nodes"])
    children, _, _, _ = read_edges(narrowing["edges"], nodes)
    lines, _, _ = primary_tree(nodes, children, set(nodes))
    return ["## Declared Narrowing Tree", "", "Each identity has its source-bound contract below.", "", "```text", *lines, "```", ""]


def _count(value: object) -> str:
    if not isinstance(value, Mapping):
        return "undefined"
    lower, upper = value.get("minimum"), value.get("maximum")
    return f"{lower}+" if upper is None else str(lower) if lower == upper else f"{lower}..{upper}"


def _clause(row: Mapping[str, Any]) -> str:
    if row.get("kind") == "relation_endpoint_pair":
        targets = _count(row["targets_per_source"]) if row.get("targets_per_source") is not None else "omitted"
        sources = _count(row["sources_per_target"]) if row.get("sources_per_target") is not None else "omitted"
        return (f"Host={row['source_endpoint']}; Target={row['target_endpoint']}; "
                f"targets per source={targets}; sources per target={sources}")
    if row.get("kind") == "relation_cardinality":
        relation = row.get("relation") or row.get("relation_notation") or "relation"
        written = row.get("written_direction", "forward")
        if row.get("target_selector") is None:
            return f"`{row.get('source_selector')}` — {relation}; outgoing count={_count(row.get('source_cardinality'))}; target domain unresolved from this clause; written direction={written}"
        return f"`{row.get('source_selector')}` — {relation} → `{row.get('target_selector')}`; Host={_count(row.get('source_cardinality'))}; Target={_count(row.get('target_cardinality'))}; written direction={written}"
    if row.get("kind") == "property_constraint":
        effective = "conflict" if row.get("occurrence_conflict") else _count(row.get("effective_occurrence_cardinality"))
        written = _count(row["occurrence_cardinality"]) if row.get("occurrence_cardinality") is not None else "omitted"
        return f"`{row.get('property_selector')}` {row.get('selection')}; names={row.get('name_format')}; written names count={written}; effective names count={effective}; values={row.get('value_format')}; values count={_count(row.get('value_cardinality'))}"
    if row.get("kind") == "effective_value_fallback_chain":
        lookup, project = row["branches"]
        return (f"`{row['property_selector']}` when undefined, null, or empty: nearest `{lookup['lookup_property']}` "
                f"via `{lookup['lookup_relation']}`, then `{project['project_property']}` "
                f"from one `{project['project_entity']}`")
    if row.get("kind") == "population_unique_constraint":
        text = f"`{row['population_selector']}`: unique {', '.join(row['keys'])}"
        if "status" in row:
            text += f" for {row['status']} states with one value for {', '.join(row['single_value_paths'])}"
        return text
    if row.get("kind") == "population_functional_dependency":
        groups = f"; Status Group in ({', '.join(row['status_groups'])})" if "status_groups" in row else ""
        return f"`{row['population_selector']}`: {', '.join(row['keys'])} determines {', '.join(row['dependents'])}{groups}"
    if row.get("kind") == "native_population_constraint":
        return f"Population count={_count(row.get('cardinality'))}; scope={row.get('scope')}"
    if row.get("kind") == "native_class":
        return f"Class {row.get('class_name')} inherits {', '.join(row.get('bases', ())) }"
    if row.get("kind") == "allowed_literal":
        return f"`{row.get('property_selector')}: {row.get('literal')}`"
    if row.get("kind") == "axis_allowed_value":
        return f"`{row.get('subject_selector')} >| {row.get('axis')}: {row.get('value')}`"
    if row.get("kind") == "axis_condition":
        return f"`{row.get('subject_selector')} >| {row.get('axis')} {row.get('operator')} {row.get('value')}`"
    return f"`{row.get('expression')}`"


def _fence(block: Mapping[str, Any]) -> list[str]:
    if str(block.get("label", "")).casefold() == "python":
        content = str(block["block"])
        marker = "`" * max([3] + [len(value) + 1 for value in re.findall(r"`+", content)])
        rows = content.split("\n")
        if rows[-1] == "":
            rows.pop()
        return [marker + str(block["label"]), *rows, marker]
    content = str(block["block"]).rstrip()
    marker = "`" * max([3] + [len(value) + 1 for value in re.findall(r"`+", content)])
    label = str(block.get("label", ""))
    status = "" if block.get("closed", True) else " (unclosed in source)"
    return [marker + label, content, marker + status]


def _render_entry(lines: list[str], entry: Record, label: str) -> None:
    lines.append(f"- {label}: `{_source_ref(entry['source'])}`")
    if entry["claim_scope"]:
        lines.extend(["  - Claim Scope:", *["    " + row if row else "" for row in entry["claim_scope"].splitlines()]])
    if entry["prose"]:
        lines.extend(["  - Remaining Claim prose:", *["    " + row if row else "" for row in entry["prose"].splitlines()]])
    for block in entry["blocks"]:
        lines.extend(["  - Fenced Claim block:", *_fence(block)])
    groups: dict[str, list[str]] = {"Value contracts": [], "Nested Property contracts": [], "Allowed values": [], "Allowed Relations and other formal clauses": []}
    for clause in entry["clauses"]:
        title = ("Value contracts" if clause.get("kind") == "property_constraint" and clause.get("selection") == "values"
                 else "Nested Property contracts" if clause.get("kind") == "property_constraint"
                 else "Allowed values" if clause.get("kind") == "allowed_literal"
                 else "Allowed Relations and other formal clauses")
        groups[title].append(_clause(clause))
    for title, values in groups.items():
        if values:
            lines.extend([f"  - {title}:", *["    - " + value for value in values]])
    if entry["instance_clauses"]:
        lines.extend(["  - Instance constraints:", *["    - " + _clause(row) for row in entry["instance_clauses"]]])
    for diagnostic in entry["diagnostics"]:
        lines.append(f"  - Unresolved Python Formal Claim: `{diagnostic.get('expression', diagnostic.get('message'))}`")
    if entry["semantics"]:
        lines.extend(["  - Semantics:", *["    " + row if row else "" for row in entry["semantics"].splitlines()]])
    if entry["details"]:
        lines.extend(["  - Details (source-bound):", *["    " + row if row else "" for row in entry["details"].splitlines()]])


def _render_contract_rows(lines: list[str], row: Record) -> None:
    for own in row["own"]:
        _render_entry(lines, own, "Declaration source")
    for shared in row["shared"]:
        binding = shared.get("binding", "exact")
        _render_entry(lines, shared, f"Shared RMED source ({binding} binding)")
        if shared.get("binding_context"):
            lines.extend(["  - Binding context:", *[
                f"    - {key.replace('_', ' ')}: `{value}`"
                for key, value in shared["binding_context"].items()
            ]])


def render_contract_graph(graph: Mapping[str, Any]) -> str:
    """Render complete source-bound Claims and bounded structured contract views."""

    lines = ["# Formal Contract Graph", "",
             "Source-bound extraction of Python Formal Claims. Authored blocks are preserved as evidence.",
             "", "## Coverage", ""]
    lines.extend(f"- {key.replace('_', ' ')}: {value}" for key, value in graph["coverage"].items())
    lines.extend([f"- display coverage: {graph['display_coverage']}", f"- structured Claim extraction: {graph['structured_claims']}"])
    lines.extend([""] + _tree_lines(graph["narrowing_tree"]))
    _render_entities(lines, graph)
    _render_relations(lines, graph)
    _render_gaps(lines, graph)
    return "\n".join(lines) + "\n"


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
            lines.append("- Transitive ancestor Declarations; their contracts are not copied:")
            lines.extend(f"  - `{row['target']}` — {', '.join(row['declaration_refs']) or 'no direct declaration source in selection'}" for row in entity["transitive_ancestors"])
        if entity["kind"] == "instance":
            instance_of = entity["instance_of"]
            lines.append(
                "- INSTANCE_OF declared Kind effective contracts; no instance contract is copied: "
                f"`{instance_of['target'] or 'unresolved'}` — "
                f"{', '.join(instance_of['effective_source_refs']) or 'no declared Kind source in selection'}"
            )
        if entity.get("inherited_property_declarations"):
            lines.append("- Inherited Property Declaration refs; no child Property Node is created:")
            lines.extend(f"  - `{row['target']}` — {', '.join(row['declaration_refs'])}" for row in entity["inherited_property_declarations"])
        _render_contract_rows(lines, entity)
        lines.append("")
    lines.extend(["## CFEL, Carrier, and Term Component Contracts", ""])
    for component in graph["components"]:
        lines.extend([f"### `{component['target']}` — declared component", ""])
        _render_contract_rows(lines, component)
        lines.append("")


def _render_relations(lines, graph):
    lines.extend(["## Relation Contracts", ""])
    for relation in graph["relations"]:
        lines.extend([f"### `(({relation['target']}))` — declared Relation", ""])
        _render_contract_rows(lines, relation)
        if relation["host_target"]:
            lines.extend(["- Host / Target contracts:", *["  - " + _clause(row) for row in relation["host_target"]]])
        if relation["metadata"]:
            lines.extend(["- Standalone metadata:", *[f"  - {row['kind']}: `{row['value']}` — {_source_ref(row['source'])}" for row in relation["metadata"]]])
        if relation.get("derived_view"):
            derived = relation["derived_view"]
            lines.append(f"- Derived view of `{derived['direct_relation']}` — {_source_ref(derived['source'])}; endpoints are a reversed source view, not new permissions.")
            lines.extend(f"  - `{endpoint['host']}` → `{endpoint['target']}`" for endpoint in derived["endpoints"])
            lines.extend(["  - Source meaning:", *["    " + line if line else "" for line in derived["meaning"].splitlines()]])
        for derived in relation.get("derived_aliases", []):
            lines.append(f"- Derived Relation `(({derived['name']}))` — {_source_ref(derived['source'])}; reverse view of the same Relation.")
            lines.extend(f"  - `{endpoint['host']}` → `{endpoint['target']}`; targets per source={_count(endpoint['targets_per_source'])}; sources per target={_count(endpoint['sources_per_target'])}" for endpoint in derived["endpoints"])
        if relation.get("derivation_scope"):
            lines.append(f"- Derivation interpretation gap: {relation['derivation_scope']}")
        for kind in ("HAS_INVERSE", "IS_INVERSE_ALIAS_FOR"):
            bindings = [row for row in relation["inverses"] if row.get("relation", "HAS_INVERSE") == kind]
            if bindings:
                lines.extend([f"- {kind} bindings; this does not certify an undeclared inverse Relation:", *[f"  - `(({row['name']}))` — {_source_ref(row['source'])}" for row in bindings]])
        if relation["derivation_links"]:
            lines.extend(["- IS_DERIVED_RELATION_OF bindings:", *[f"  - `(({row['name']}))` — {_source_ref(row['source'])}" for row in relation["derivation_links"]]])
        lines.append("")


def _render_gaps(lines, graph):
    lines.extend(["## Coverage Gaps and Conflicts", ""])
    for row in graph["coverage_gaps"]:
        lines.append(f"- `{_source_ref(row['source'])}`: {row['message']}")
        _render_entry(lines, row, "Unbound source evidence")
    for row in graph["outside_model_scope"]:
        lines.append(f"- `{_source_ref(row['source'])}`: {row['message']}")
        _render_entry(lines, row, "Selected evidence outside model scope")
    for row in graph["conflicts"]:
        lines.append(f"- Duplicate {row['kind']} Declaration `{row['target']}`: {', '.join(row['sources'])}")
    for row in graph["missing_relation_semantics"]:
        lines.append(f"- Relation `(({row['relation']}))` lacks Semantics: `{_source_ref(row['source'])}`")
    for row in graph["instance_kind_gaps"]:
        lines.append(f"- Instance `{row['instance']}` has no declared Kind target: `{row['kind'] or 'unresolved'}`")
    for row in graph["diagnostics"]:
        lines.append(f"- `{_source_ref(row['source'])}`: {row.get('expression', row.get('message'))}")
    for message in graph["inheritance_diagnostics"]:
        lines.append(f"- Narrowing evidence: {message}")
    if not (graph["coverage_gaps"] or graph["conflicts"] or graph["missing_relation_semantics"] or graph["instance_kind_gaps"] or graph["diagnostics"] or graph["inheritance_diagnostics"]):
        lines.append("- None.")
