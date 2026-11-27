"""Source-bound subject projections without executing Claim code."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from ._subject_projection_contexts import (
    Any as Any,
    _subject_Name as _subject_Name,
    _subject_Path as _subject_Path,
    _subject_RelationChain as _subject_RelationChain,
    _subject_SubjectNotationError as _subject_SubjectNotationError,
    _subject_namespace_local_expression as _subject_namespace_local_expression,
    _subject_parse_subject_expression as _subject_parse_subject_expression,
    carrier_read_view as carrier_read_view,
    matches_named_value as matches_named_value,
    _source_ref as _source_ref,
    _view as _view,
    _ancestors as _ancestors,
    _detail_declarations as _detail_declarations,
    _namespace_candidate as _namespace_candidate,
    _namespace_contexts as _namespace_contexts,
    _rule_groups as _rule_groups,
)
from .contract_graph import (
    compose_contract_graph,
)
from .current_subject_graph import (
    compose_narrowing_graph,
)
from .declaration_evidence import (
    Record,
)
from .subject_projection_properties import (
    _formal_claims,
    _property_record,
    _resolve_property_formats,
    _source_rows,
)
from .subject_projection_relations import (
    _relation_declarations,
    _relations_by_origin,
)


def _primary_declarations(
    tree: Record, contracts: Record
) -> dict[str, Record]:
    tree_identities = {node["identity"] for node in tree["nodes"]}
    return {
        row["target"]: row
        for row in [
            *[
                row
                for row in contracts["entities"]
                if row["kind"] == "primary_node"
            ],
            *[
                row
                for row in contracts["components"]
                if row["target"] in tree_identities
            ],
        ]
    }


def _projection_properties(
    contracts: Record,
) -> tuple[list[Record], dict[str, list[Record]], list[Record]]:
    property_rows = [
        row for row in contracts["entities"] if row["kind"] == "property"
    ]
    properties = [
        property
        for row in property_rows
        if (property := _property_record(row)) is not None
    ]
    format_diagnostics = _resolve_property_formats(
        properties,
        [
            entry
            for row in [*contracts["entities"], *contracts["components"]]
            for entry in row["own"]
        ],
    )
    properties_by_origin: dict[str, list[Record]] = defaultdict(list)
    for property in properties:
        properties_by_origin[property["origin_entity"]].append(property)
    return property_rows, properties_by_origin, format_diagnostics


def _entity_properties(
    identity: str,
    lineage: list[str],
    class_names: Mapping[str, set[str]],
    properties_by_origin: Mapping[str, list[Record]],
) -> tuple[list[Record], list[Record]]:
    names = set().union(
        *(class_names.get(path, set()) for path in [identity, *lineage])
    )

    def applies(scope) -> bool:
        return not scope or bool(names.intersection(scope))

    def property_for_entity(property: Record, *, inherited: bool) -> Record:
        contracts = [
            clause
            for clause in property["contracts"]
            if applies(clause.get("ordering_roles"))
        ]
        return {**property, "inherited": inherited, "contracts": contracts}

    direct = [
        property_for_entity(property, inherited=False)
        for property in properties_by_origin.get(identity, [])
        if applies(property.get("applicable_entity_classes"))
    ]
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
    tree: Record,
    primary_rows: Mapping[str, Record],
    properties_by_origin: Mapping[str, list[Record]],
    relations_by_origin: Mapping[str, list[Record]],
) -> list[Record]:
    ancestors = _ancestors(tree)
    class_names = {
        target: {
            clause["class_name"]
            for entry in row["own"]
            for clause in entry["clauses"]
            if clause.get("kind") == "native_class"
        }
        for target, row in primary_rows.items()
    }
    entities = []
    for node in sorted(tree["nodes"], key=lambda row: row["identity"]):
        entities.append(
            _project_entity(
                node,
                primary_rows,
                ancestors,
                class_names,
                properties_by_origin,
                relations_by_origin,
            )
        )
    return entities


def _projection_declarations(
    contracts: Record,
    primary_rows: Mapping[str, Record],
    property_rows: list[Record],
) -> Record:
    return {
        "primary_nodes": {
            target: row["own"] for target, row in primary_rows.items()
        },
        "properties": {row["target"]: row["own"] for row in property_rows},
        "instances": {
            row["target"]: row["own"]
            for row in contracts["entities"]
            if row["kind"] == "instance"
        },
        "relations": {
            row["target"]: row["own"] for row in contracts["relations"]
        },
        "components": {
            row["target"]: row["own"] for row in contracts["components"]
        },
        "namespaces": {
            row["target"]: row["own"] for row in contracts["namespaces"]
        },
    }


def build_subject_projection_data(carriers: list[Record]) -> Record:
    """Build additive source-bound views from the supplied Current frontier.
    Tree admission uses all supplied carriers. Property contracts and formal
    claims use only exact Requirement / Declaration carriers before Claim
    extraction, so no other RMED body becomes declaration authority.
    """
    tree, tree_provenance = compose_narrowing_graph(carriers)
    detail_carriers = _detail_declarations(carriers)
    contracts = compose_contract_graph(detail_carriers)
    projection = _projection_properties(contracts)
    property_rows, properties_by_origin, format_diagnostics = projection
    primary_rows = _primary_declarations(tree, contracts)
    relation_declarations = _relation_declarations(contracts["relations"])
    relations_by_origin = _relations_by_origin(
        contracts["relations"], relation_declarations, primary_rows
    )
    entities = _project_entities(
        tree, primary_rows, properties_by_origin, relations_by_origin
    )
    return {
        "tree": tree,
        "tree_provenance": tree_provenance,
        "namespaces": _namespace_contexts(carriers),
        "entities": entities,
        "relation_declarations": relation_declarations,
        "declarations": _projection_declarations(
            contracts, primary_rows, property_rows
        ),
        "diagnostics": [
            *contracts["diagnostics"],
            *format_diagnostics,
            *[
                {"code": "duplicate_exact_declaration", **conflict}
                for conflict in contracts["conflicts"]
            ],
        ],
        "coverage": {
            **contracts["coverage"],
            "tree_entities": len(entities),
            "detail_declaration_sources": len(detail_carriers),
            "entities_without_exact_declaration": sum(
                not entity["declaration_refs"] for entity in entities
            ),
        },
    }


def _project_entity(
    node,
    primary_rows,
    ancestors,
    class_names,
    properties_by_origin,
    relations_by_origin,
):
    identity = node["identity"]
    own = primary_rows.get(identity, {}).get("own", [])
    sources, refs = _source_rows(own)
    direct, inherited = _entity_properties(
        identity,
        ancestors.get(identity, []),
        class_names,
        properties_by_origin,
    )
    relations = [
        relation
        for origin in [identity, *ancestors.get(identity, [])]
        for relation in relations_by_origin.get(origin, [])
    ]
    property_origins = _rule_groups(
        identity,
        [*direct, *inherited],
        ancestors,
        lambda row: row["relative_name"],
    )
    relation_origins = _rule_groups(
        identity,
        relations,
        ancestors,
        lambda row: (row["relation"], row["level"], row["direction"]),
    )
    return {
        "identity": identity,
        "source_refs": sources,
        "declaration_refs": refs,
        "ancestors": ancestors.get(identity, []),
        "direct_properties": direct,
        "inherited_properties": inherited,
        "formal_claims": _formal_claims(own),
        "property_rule_origins": property_origins,
        "relation_rule_origins": relation_origins,
    }
