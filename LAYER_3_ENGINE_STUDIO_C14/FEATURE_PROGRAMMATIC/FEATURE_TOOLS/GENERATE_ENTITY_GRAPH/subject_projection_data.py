"""Source-bound subject projections without CFEL evaluation."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30 import subject_notation__pub as notation
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carrier_compat__pub import carrier_read_view, matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph import compose_contract_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_common import _source_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_graph import compose_narrowing_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.declaration_evidence import Record, _view
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_projection_properties import (
    _formal_claims,
    _property_record,
    _resolve_property_formats,
    _source_rows,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.subject_projection_relations import _relation_declarations, _relations_by_origin


def _detail_declarations(carriers: list[Record]) -> list[Record]:
    """Admit only the exact Current declaration role/form for property detail."""

    return [
        carrier for carrier in carriers
        if matches_named_value(_view(carrier).get("content_role"), "Requirement") and any(
            matches_named_value(_view(carrier).get("type"), form)
            for form in ("Declaration", "Relation Declaration")
        )
    ]


def _ancestors(tree: Mapping[str, Any]) -> dict[str, list[str]]:
    nodes = {row["id"]: row["identity"] for row in tree["nodes"]}
    parents: dict[str, list[str]] = defaultdict(list)
    for edge in tree["edges"]:
        parents[nodes[edge["relation_source"]]].append(nodes[edge["relation_target"]])

    def collect(identity: str, seen: frozenset[str] = frozenset()) -> list[str]:
        result: list[str] = []
        for parent in parents.get(identity, []):
            if parent not in seen:
                result.append(parent)
                result.extend(collect(parent, seen | {parent}))
        return list(dict.fromkeys(result))

    return {identity: collect(identity) for identity in nodes.values()}


def _rule_groups(identity: str, rules: list[Record], ancestors: Mapping[str, list[str]], key) -> Record:
    """Group rules without selecting between unrelated inherited declarations."""
    grouped: Record = {"declared_here": [], "inherited": [], "overridden_here": []}
    for rule in rules:
        origin = rule["origin_entity"]
        matching = [other for other in rules
                    if key(other) == key(rule) and other["origin_entity"] != origin]
        replaced = [other for other in matching if other["origin_entity"] in ancestors.get(origin, [])]
        if any(origin in ancestors.get(other["origin_entity"], []) for other in matching):
            continue
        item = {**rule, "replaces": [
            {"identity": old.get("identity"), "origin_entity": old["origin_entity"], "declaration_refs": old["declaration_refs"],
             "source_refs": old["source_refs"], "contract": old.get("contract"),
             "contracts": old.get("contracts")}
            for old in replaced
        ]}
        if origin == identity:
            group = "overridden_here" if replaced else "declared_here"
        else:
            group = "inherited"
        grouped[group].append(item)
    return grouped


def _namespace_contexts(carriers: list[Record]) -> list[Record]:
    """Keep one explicit ANECHOIC root context per namespace branch."""

    candidates: dict[str, list[tuple[int, Record]]] = defaultdict(list)
    for carrier in carriers:
        source = carrier.get("source")
        subjects = carrier.get("subjects")
        if not isinstance(source, Mapping) or not isinstance(subjects, Mapping):
            continue
        try:
            normalized = carrier_read_view({"subjects": dict(subjects)})["subjects"]
        except ValueError:
            continue
        for role in ("governs", "depends_on"):
            values = normalized.get(role, [])
            for subject in values if isinstance(values, list) else [values]:
                if not isinstance(subject, str):
                    continue
                try:
                    expression = notation.parse_subject_expression(subject, subject_profile="approved").expression
                except notation.SubjectNotationError:
                    continue
                if (isinstance(expression, notation.Path) and isinstance(expression.head, notation.Name)
                        and expression.head.value in {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}
                        and not expression.steps):
                    candidates[expression.head.value].append((0 if role == "governs" else 1, dict(source)))
                    continue
                local = notation.namespace_local_expression(expression)
                if local is None or not isinstance(expression, notation.RelationChain):
                    continue
                first = expression.endpoints[0]
                if isinstance(first.head, notation.Name) and first.head.value in {"ANECHOIC_MODEL", "ANECHOIC_STRUCTURE"}:
                    candidates[first.head.value].append((2, dict(source)))
                    continue
                namespace = expression.endpoints[1]
                if not isinstance(namespace.head, notation.Name):
                    continue
                root = f"ANECHOIC <+ {namespace.head.value}"
                direct = len(expression.endpoints) == 2
                priority = 0 if direct and role == "governs" else 1 if direct else 2
                candidates[root].append((priority, dict(source)))
    return [
        {"subject": root, "source": source}
        for root, rows in sorted(candidates.items())
        for _, source in [min(rows, key=lambda row: (row[0], _source_ref(row[1]), str(row[1].get("path", ""))))]
    ]


def _primary_declarations(tree: Record, contracts: Record) -> dict[str, Record]:
    tree_identities = {node["identity"] for node in tree["nodes"]}
    return {
        row["target"]: row for row in [
            *[row for row in contracts["entities"] if row["kind"] == "primary_node"],
            *[row for row in contracts["components"] if row["target"] in tree_identities],
        ]
    }


def _projection_properties(
    contracts: Record,
) -> tuple[list[Record], dict[str, list[Record]], list[Record]]:
    property_rows = [row for row in contracts["entities"] if row["kind"] == "property"]
    properties = [property for row in property_rows if (property := _property_record(row)) is not None]
    format_diagnostics = _resolve_property_formats(
        properties, [entry for row in [*contracts["entities"], *contracts["components"]] for entry in row["own"]],
    )
    properties_by_origin: dict[str, list[Record]] = defaultdict(list)
    for property in properties:
        properties_by_origin[property["origin_entity"]].append(property)
    return property_rows, properties_by_origin, format_diagnostics


def _entity_properties(
    identity: str, lineage: list[str], class_names: Mapping[str, set[str]],
    properties_by_origin: Mapping[str, list[Record]],
) -> tuple[list[Record], list[Record]]:
    names = set().union(*(class_names.get(path, set()) for path in [identity, *lineage]))

    def applies(scope) -> bool:
        return not scope or bool(names.intersection(scope))

    def property_for_entity(property: Record, *, inherited: bool) -> Record:
        contracts = [clause for clause in property["contracts"] if applies(clause.get("ordering_roles"))]
        return {**property, "inherited": inherited, "contracts": contracts}

    direct = [property_for_entity(property, inherited=False)
              for property in properties_by_origin.get(identity, [])
              if applies(property.get("applicable_entity_classes"))]
    inherited = [
        property_for_entity(property, inherited=True)
        for ancestor in lineage
        for property in properties_by_origin.get(ancestor, [])
        if applies(property.get("applicable_entity_classes"))
    ]
    slots: dict[str, int] = defaultdict(int)
    for property in [*direct, *inherited]:
        slots[property["relative_name"]] += 1
    for property in [*direct, *inherited]:
        if slots[property["relative_name"]] > 1:
            property["multiple_applicable"] = True
    return direct, inherited


def _project_entities(
    tree: Record, primary_rows: Mapping[str, Record], properties_by_origin: Mapping[str, list[Record]],
    relations_by_origin: Mapping[str, list[Record]],
) -> list[Record]:
    ancestors = _ancestors(tree)
    class_names = {
        target: {clause["class_name"] for entry in row["own"] for clause in entry["clauses"]
                 if clause.get("kind") == "native_class"}
        for target, row in primary_rows.items()
    }
    entities = []
    for node in sorted(tree["nodes"], key=lambda row: row["identity"]):
        identity = node["identity"]
        own = primary_rows.get(identity, {}).get("own", [])
        sources, refs = _source_rows(own)
        direct, inherited = _entity_properties(
            identity, ancestors.get(identity, []), class_names, properties_by_origin,
        )
        relations = [relation for origin in [identity, *ancestors.get(identity, [])]
                     for relation in relations_by_origin.get(origin, [])]
        property_origins = _rule_groups(identity, [*direct, *inherited], ancestors,
                                        lambda row: row["relative_name"])
        relation_origins = _rule_groups(identity, relations, ancestors,
                                        lambda row: (row["relation"], row["level"], row["direction"]))
        entities.append({
            "identity": identity, "source_refs": sources, "declaration_refs": refs,
            "ancestors": ancestors.get(identity, []), "direct_properties": direct,
            "inherited_properties": inherited, "formal_claims": _formal_claims(own),
            "property_rule_origins": property_origins, "relation_rule_origins": relation_origins,
        })
    return entities


def _projection_declarations(
    contracts: Record, primary_rows: Mapping[str, Record], property_rows: list[Record],
) -> Record:
    return {
        "primary_nodes": {target: row["own"] for target, row in primary_rows.items()},
        "properties": {row["target"]: row["own"] for row in property_rows},
        "instances": {
            row["target"]: row["own"] for row in contracts["entities"] if row["kind"] == "instance"
        },
        "relations": {row["target"]: row["own"] for row in contracts["relations"]},
        "components": {row["target"]: row["own"] for row in contracts["components"]},
        "namespaces": {row["target"]: row["own"] for row in contracts["namespaces"]},
    }


def build_subject_projection_data(carriers: list[Record]) -> Record:
    """Build additive source-bound views from the supplied Current frontier.

    Tree admission uses all supplied carriers. Property contracts and formal
    claims use only exact Requirement / Declaration carriers before CFEL
    extraction, so no other RMED body becomes declaration authority.
    """
    tree, tree_provenance = compose_narrowing_graph(carriers)
    detail_carriers = _detail_declarations(carriers)
    contracts = compose_contract_graph(detail_carriers)
    property_rows, properties_by_origin, format_diagnostics = _projection_properties(contracts)
    primary_rows = _primary_declarations(tree, contracts)
    relation_declarations = _relation_declarations(contracts["relations"])
    relations_by_origin = _relations_by_origin(contracts["relations"], relation_declarations, primary_rows)
    entities = _project_entities(tree, primary_rows, properties_by_origin, relations_by_origin)

    return {
        "tree": tree, "tree_provenance": tree_provenance, "namespaces": _namespace_contexts(carriers), "entities": entities,
        "relation_declarations": relation_declarations,
        "declarations": _projection_declarations(contracts, primary_rows, property_rows),
        "diagnostics": [
            *contracts["diagnostics"],
            *format_diagnostics,
            *[
                {"code": "duplicate_exact_declaration", **conflict}
                for conflict in contracts["conflicts"]
            ],
        ],
        "coverage": {
            **contracts["coverage"], "tree_entities": len(entities),
            "detail_declaration_sources": len(detail_carriers),
            "entities_without_exact_declaration": sum(not entity["declaration_refs"] for entity in entities),
        },
    }
