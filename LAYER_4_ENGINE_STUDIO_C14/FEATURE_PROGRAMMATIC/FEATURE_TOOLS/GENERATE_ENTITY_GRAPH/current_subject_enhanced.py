"""Compose a syntax graph from supplied current Atom Subjects, without history."""



from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
    render_subject as _subject_render_subject,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import (
    Record, _identifier, _is_declaration, _model_target,
    _relation_definition_target, _target_kind, _view, _is_relation_definition,
    namespace_local_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_base import compose_current_graph

def _declaration_row(
    target: str, occurrence: Record, kind: str,
) -> Record:
    return {
        "identity": target,
        "source": occurrence["source"],
        "subject": occurrence["subject"],
        "declaration_kind": kind,
    }


def _declared_target(carrier, occurrence, expression):
    if _is_relation_definition(carrier):
        admitted = _relation_definition_target(expression)
        if admitted is None:
            return None
        target, kind = admitted
    elif _is_declaration(carrier):
        local_expression = namespace_local_expression(expression)
        if local_expression is not None:
            expression = local_expression
        elif isinstance(expression, _subject_RelationChain):
            return None
        kind = _target_kind(expression)
        if kind is None:
            return None
        assert isinstance(expression, _subject_Path)
        target = _model_target(expression)
        if kind == "instance" and target.startswith("Node/") and "//" in target:
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import extract_claim_constraints
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import model_class_target
            clauses, _ = extract_claim_constraints(carrier)
            if any(clause.get("kind") == "native_class" and
                   model_class_target(occurrence["subject"], clause.get("entity_name")) == target
                   for clause in clauses):
                kind = "primary_node"
    else:
        return None
    return target, kind


def _add_category(occurrence, carrier_by_path, active_count, categories, diagnostics):
    source = occurrence["source"]
    categories["selected_subject_expressions"].append({
        "expression": occurrence["subject"],
        "subject_role": occurrence["role"],
        "source": source,
    })
    carrier = carrier_by_path.get(source["path"])
    if (carrier is None or occurrence["role"] != "governs"
            or active_count[source["path"]] != 1):
        return
    try:
        expression = _subject_parse_subject_expression(
            occurrence["subject"], subject_profile="approved"
        ).expression
    except _subject_SubjectNotationError as error:
        diagnostics.append(
            f"{occurrence['id']}: Model target unavailable: {error}"
        )
        return
    admitted = _declared_target(carrier, occurrence, expression)
    if admitted is None:
        return
    target, kind = admitted
    bucket = {
        "primary_node": "primary_nodes", "property": "properties",
        "instance": "instances", "relation": "relations",
    }[kind]
    categories[bucket].append(_declaration_row(target, occurrence, kind))


def _enhanced_categories(
    carriers: list[Record], provenance: Record, diagnostics: list[str],
) -> Record:
    """Separate declared model targets from arbitrary Subject expressions.

    A Subject path can select, filter or constrain an existing Node. It becomes
    a model inventory entry only when it is the direct active target of a
    Requirement / Declaration Atom. This intentionally leaves raw syntax
    nodes in the legacy graph for lossless rendering without treating them as
    admitted model nodes.
    """

    carrier_by_path = {
        carrier["source"]["path"]: carrier
        for carrier in carriers
        if isinstance(carrier.get("source"), dict) and isinstance(carrier["source"].get("path"), str)
    }
    categories: dict[str, list[Record]] = {
        "primary_nodes": [], "properties": [], "instances": [], "relations": [],
        "classifications": [], "allowed_literals": [], "selected_subject_expressions": [],
    }
    active_count = {
        source_path: sum(
            occurrence["role"] == "governs" and occurrence["source"]["path"] == source_path
            for occurrence in provenance["occurrences"]
        )
        for source_path in carrier_by_path
    }
    for occurrence in provenance["occurrences"]:
        _add_category(occurrence, carrier_by_path, active_count, categories, diagnostics)
    return {
        key: sorted(values, key=lambda row: (str(row.get("identity", row.get("expression", row.get("source", "")))), str(row)))
        for key, values in categories.items()
    }


def _formal_relations(constraints, declared, provenance, nodes, edges):
    formal_relations: dict[str, Record] = {}
    for index, clause in enumerate(constraints):
        selector = clause.get("source_selector")
        if (not declared(clause) or clause.get("kind") != "relation_cardinality"
                or clause.get("relation") != "IS_INSTANCE_OF"
                or not isinstance(selector, str) or not selector.startswith("(") or not selector.endswith(")")
                or clause.get("source_cardinality") is not None or clause.get("target_cardinality") is not None):
            continue
        try:
            parsed = _subject_parse_subject_expression(selector[1:-1], subject_profile="approved").expression
            target = _subject_parse_subject_expression(clause["target_selector"], subject_profile="approved").expression
        except (_subject_SubjectNotationError, TypeError):
            continue
        if not isinstance(parsed, _subject_RelationChain) or not isinstance(target, _subject_Path):
            continue
        source_identity, target_identity = _subject_render_subject(parsed), _subject_render_subject(target)
        occurrence_id = f"{clause['source'].get('path', '')}#formal_claim[{index}]"
        provenance["occurrences"].append({"id": occurrence_id, "subject": clause["expression"],
                                          "source": clause["source"], "role": "formal_claim"})
        for identity in (source_identity, target_identity):
            node_id = _identifier("subject:", identity)
            node = nodes.setdefault(node_id, {"identity": identity, "id": node_id,
                                               "occurrence_ids": [], "is_full_target": False})
            node["occurrence_ids"] = sorted(set(node["occurrence_ids"]) | {occurrence_id})
        source_id, target_id = (_identifier("subject:", identity) for identity in (source_identity, target_identity))
        metadata = {"kind": "IS_INSTANCE_OF", "forward_cardinality": None, "reverse_cardinality": None}
        edge_id = _identifier("subject-edge:", [metadata, source_id, target_id])
        edge = edges.setdefault(edge_id, {**metadata, "id": edge_id, "relation_source": source_id,
                                          "relation_target": target_id, "occurrence_ids": []})
        edge["occurrence_ids"] = sorted(set(edge["occurrence_ids"]) | {occurrence_id})
        relation = formal_relations.setdefault(edge_id, {"kind": "IS_INSTANCE_OF", "source": source_identity,
                                                          "target": target_identity, "occurrence_ids": []})
        relation["occurrence_ids"] = sorted(set(relation["occurrence_ids"]) | {occurrence_id})
    return formal_relations


def _source_sets(carriers):
    declaration_sources = {
        (carrier["source"].get("atom_id"), carrier["source"].get("version"), carrier["source"].get("path"))
        for carrier in carriers if isinstance(carrier.get("source"), dict) and _is_declaration(carrier)
    }
    identified_sources = {
        (carrier["source"].get("atom_id"), carrier["source"].get("version"), carrier["source"].get("path"))
        for carrier in carriers if isinstance(carrier.get("source"), dict) and _view(carrier).get("type")
    }
    return declaration_sources, identified_sources


def compose_enhanced_current_graph(carriers: list[Record]) -> tuple[Record, Record]:
    """Add model/instance and CFEL inventories to the stable Subject graph.

    These records are source-bound observations.  They intentionally do not
    evaluate CFEL, synthesize inherited facts, or turn literals and constraint
    annotations into graph Nodes.
    """

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import claim_cfel_blocks, claim_python_blocks, constraints_for

    graph, provenance = compose_current_graph(carriers, unsupported_as_diagnostics=True)
    constraints, unresolved = constraints_for(carriers)
    declaration_sources, identified_sources = _source_sets(carriers)
    def declared(row: Record) -> bool:
        source = row.get("source", {})
        return (source.get("atom_id"), source.get("version"), source.get("path")) in declaration_sources
    def non_declaration_property(row: Record) -> bool:
        source = row.get("source", {})
        key = (source.get("atom_id"), source.get("version"), source.get("path"))
        return (row.get("kind") in {"property_constraint", "allowed_literal"}
                and key in identified_sources and not declared(row))
    model_constraints = [row for row in constraints if row.get("group") != "instances" and not non_declaration_property(row)]
    model = _enhanced_categories(carriers, provenance, graph["diagnostics"])
    nodes = {row["id"]: row for row in graph["nodes"]}
    edges = {row["id"]: row for row in graph["edges"]}
    formal_relations = _formal_relations(constraints, declared, provenance, nodes, edges)
    model["relations"].extend(sorted(formal_relations.values(), key=lambda row: (row["source"], row["target"])))
    graph["nodes"] = sorted(nodes.values(), key=lambda row: (row["identity"], row["id"]))
    graph["edges"] = sorted(edges.values(), key=lambda row: row["id"])
    enhanced = {
        **graph,
        "kind": "current_atom_model_graph",
        "model": model,
        "constraints": model_constraints,
        "model_contracts": [row for row in model_constraints
                            if row.get("kind") in {"property_constraint", "allowed_literal"} and declared(row)],
        "source_constraints": [row for row in constraints if row.get("group") != "instances" and non_declaration_property(row)],
        "instance_constraints": [row for row in constraints if row.get("group") == "instances"],
        "formal_claim_blocks": [block for carrier in carriers for block in
                                [*claim_cfel_blocks(carrier), *claim_python_blocks(carrier)]],
        "cfel_diagnostics": unresolved,
    }
    return enhanced, provenance
