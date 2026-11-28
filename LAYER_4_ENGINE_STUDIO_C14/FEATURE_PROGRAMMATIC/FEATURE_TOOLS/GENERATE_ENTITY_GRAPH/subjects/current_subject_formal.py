"""Project explicit formal Relation claims into the Subject graph."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    subjects.current_subject_common import (
    Record, _identifier, _is_declaration, _view,
)  # fmt: skip


def _formal_relations(constraints, declared, provenance, nodes, edges):
    formal_relations: dict[str, Record] = {}
    for index, clause in enumerate(constraints):
        _add_formal_relation(
            index, clause, declared, provenance, nodes, edges, formal_relations
        )
    return formal_relations


def _add_formal_relation(
    index, clause, declared, provenance, nodes, edges, formal_relations
):
    selector = clause.get("source_selector")
    if (
        not declared(clause)
        or clause.get("kind") != "relation_cardinality"
        or clause.get("relation") != "INSTANCE_OF"
        or not isinstance(selector, str)
        or not selector.startswith("(")
        or not selector.endswith(")")
        or clause.get("source_cardinality") is not None
        or clause.get("target_cardinality") is not None
    ):
        return
    try:
        parsed = _subject_parse_subject_expression(
            selector[1:-1], subject_profile="approved"
        ).expression
        target = _subject_parse_subject_expression(
            clause["target_selector"], subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError, TypeError:
        return
    if not isinstance(parsed, _subject_RelationChain) or not isinstance(
        target, _subject_Path
    ):
        return
    source_identity, target_identity = (
        _subject_render_subject(parsed),
        _subject_render_subject(target),
    )
    _record_formal_relation(
        index,
        clause,
        source_identity,
        target_identity,
        provenance,
        nodes,
        edges,
        formal_relations,
    )


def _record_nodes_and_edge(
    nodes, edges, source_identity, target_identity, occurrence_id
):
    for identity in (source_identity, target_identity):
        node_id = _identifier("subject:", identity)
        node = nodes.setdefault(
            node_id,
            {
                "identity": identity,
                "id": node_id,
                "occurrence_ids": [],
                "is_full_target": False,
            },
        )
        node["occurrence_ids"] = sorted(
            set(node["occurrence_ids"]) | {occurrence_id}
        )
    source_id, target_id = (
        _identifier("subject:", identity)
        for identity in (source_identity, target_identity)
    )
    metadata = {
        "kind": "INSTANCE_OF",
        "forward_cardinality": None,
        "reverse_cardinality": None,
    }
    edge_id = _identifier("subject-edge:", [metadata, source_id, target_id])
    edge = edges.setdefault(
        edge_id,
        {
            **metadata,
            "id": edge_id,
            "relation_source": source_id,
            "relation_target": target_id,
            "occurrence_ids": [],
        },
    )
    edge["occurrence_ids"] = sorted(
        set(edge["occurrence_ids"]) | {occurrence_id}
    )
    return edge_id


def _record_formal_relation(
    index,
    clause,
    source_identity,
    target_identity,
    provenance,
    nodes,
    edges,
    formal_relations,
):
    occurrence_id = f"{clause['source'].get('path', '')}#formal_claim[{index}]"
    provenance["occurrences"].append(
        {
            "id": occurrence_id,
            "subject": clause["expression"],
            "source": clause["source"],
            "role": "formal_claim",
        }
    )
    edge_id = _record_nodes_and_edge(
        nodes, edges, source_identity, target_identity, occurrence_id
    )
    relation = formal_relations.setdefault(
        edge_id,
        {
            "kind": "INSTANCE_OF",
            "source": source_identity,
            "target": target_identity,
            "occurrence_ids": [],
        },
    )
    relation["occurrence_ids"] = sorted(
        set(relation["occurrence_ids"]) | {occurrence_id}
    )


def _source_sets(carriers):
    declaration_sources = {
        (
            carrier["source"].get("atom_id"),
            carrier["source"].get("version"),
            carrier["source"].get("path"),
        )
        for carrier in carriers
        if isinstance(carrier.get("source"), dict) and _is_declaration(carrier)
    }
    identified_sources = {
        (
            carrier["source"].get("atom_id"),
            carrier["source"].get("version"),
            carrier["source"].get("path"),
        )
        for carrier in carriers
        if isinstance(carrier.get("source"), dict)
        and _view(carrier).get("type")
    }
    return declaration_sources, identified_sources
