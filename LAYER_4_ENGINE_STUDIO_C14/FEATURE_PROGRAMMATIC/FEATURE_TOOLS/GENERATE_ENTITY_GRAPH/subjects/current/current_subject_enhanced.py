"Compose a syntax graph from supplied current Atom Subjects, without history."

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
)

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    subjects.subjects__shared import (
    Record,
    _is_declaration,
    _model_target,
    _relation_definition_target,
    _target_kind,
    _view as _view,
    _is_relation_definition,
    namespace_local_expression,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    subjects.current.current_subject_base import (
    compose_current_graph,
)  # fmt: skip


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.\
    subjects.subjects__shared import (
    _formal_relations as _formal_relations,
    _identifier as _identifier,
    _source_sets as _source_sets,
)  # fmt: skip


def _declaration_row(
    target: str,
    occurrence: Record,
    kind: str,
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
        if (
            kind == "instance"
            and target.startswith("Node/")
            and "//" in target
        ):
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
                GENERATE_ENTITY_GRAPH.claims.claims__shared import (
                extract_claim_constraints,
            )  # fmt: skip
            from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model__shared import (
                model_class_target,
            )

            clauses, _ = extract_claim_constraints(carrier)
            if any(
                clause.get("kind") == "native_class"
                and model_class_target(
                    occurrence["subject"], clause.get("entity_name")
                )
                == target
                for clause in clauses
            ):
                kind = "primary_node"
    else:
        return None
    return target, kind


def _add_category(
    occurrence, carrier_by_path, active_count, categories, diagnostics
):
    source = occurrence["source"]
    categories["selected_subject_expressions"].append(
        {
            "expression": occurrence["subject"],
            "subject_role": occurrence["role"],
            "source": source,
        }
    )
    carrier = carrier_by_path.get(source["path"])
    if (
        carrier is None
        or occurrence["role"] != "governs"
        or active_count[source["path"]] != 1
    ):
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
        "primary_node": "primary_nodes",
        "property": "properties",
        "instance": "instances",
        "relation": "relations",
    }[kind]
    categories[bucket].append(_declaration_row(target, occurrence, kind))


def _enhanced_categories(
    carriers: list[Record],
    provenance: Record,
    diagnostics: list[str],
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
        if isinstance(carrier.get("source"), dict)
        and isinstance(carrier["source"].get("path"), str)
    }
    categories: dict[str, list[Record]] = {
        "primary_nodes": [],
        "properties": [],
        "instances": [],
        "relations": [],
        "axes": [],
        "allowed_literals": [],
        "selected_subject_expressions": [],
    }
    active_count = {
        source_path: sum(
            occurrence["role"] == "governs"
            and occurrence["source"]["path"] == source_path
            for occurrence in provenance["occurrences"]
        )
        for source_path in carrier_by_path
    }
    for occurrence in provenance["occurrences"]:
        _add_category(
            occurrence, carrier_by_path, active_count, categories, diagnostics
        )
    return _sort_categories(categories)


def _sort_categories(categories):
    return {
        key: sorted(
            values,
            key=lambda row: (
                str(
                    row.get(
                        "identity",
                        row.get("expression", row.get("source", "")),
                    )
                ),
                str(row),
            ),
        )
        for key, values in categories.items()
    }


def _source_predicates(declaration_sources, identified_sources):
    def declared(row: Record) -> bool:
        source = row.get("source", {})
        return (
            source.get("atom_id"),
            source.get("version"),
            source.get("path"),
        ) in declaration_sources

    def non_declaration_property(row: Record) -> bool:
        source = row.get("source", {})
        key = (
            source.get("atom_id"),
            source.get("version"),
            source.get("path"),
        )
        return (
            row.get("kind") in {"property_constraint", "allowed_literal"}
            and key in identified_sources
            and not declared(row)
        )

    return declared, non_declaration_property


def _augment_graph(graph, model, constraints, declared, provenance):
    nodes = {row["id"]: row for row in graph["nodes"]}
    edges = {row["id"]: row for row in graph["edges"]}
    formal_relations = _formal_relations(
        constraints, declared, provenance, nodes, edges
    )
    model["relations"].extend(
        sorted(
            formal_relations.values(),
            key=lambda row: (row["source"], row["target"]),
        )
    )
    graph["nodes"] = sorted(
        nodes.values(), key=lambda row: (row["identity"], row["id"])
    )
    graph["edges"] = sorted(edges.values(), key=lambda row: row["id"])


def compose_enhanced_current_graph(
    carriers: list[Record],
) -> tuple[Record, Record]:
    """Add model/instance and Python Formal Claim inventories to the stable \
Subject graph.

    These records are source-bound observations.  They intentionally do not
    execute Python, synthesize inherited facts, or turn literals and constraint
    annotations into graph Nodes.
    """

    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claims.claims__shared import (
        constraints_for,
    )
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claims.primitives.\
        primitives__shared import (
        claim_python_blocks,
    )  # fmt: skip

    graph, provenance = compose_current_graph(
        carriers, unsupported_as_diagnostics=True
    )
    constraints, unresolved = constraints_for(carriers)
    declaration_sources, identified_sources = _source_sets(carriers)

    declared, non_declaration_property = _source_predicates(
        declaration_sources, identified_sources
    )

    model_constraints = [
        row
        for row in constraints
        if row.get("group") != "instances"
        and not non_declaration_property(row)
    ]
    model = _enhanced_categories(carriers, provenance, graph["diagnostics"])
    _augment_graph(graph, model, constraints, declared, provenance)
    return _enhanced_result(
        graph,
        model,
        model_constraints,
        constraints,
        declared,
        non_declaration_property,
        carriers,
        claim_python_blocks,
        unresolved,
    ), provenance


def _enhanced_result(
    graph,
    model,
    model_constraints,
    constraints,
    declared,
    non_declaration_property,
    carriers,
    claim_python_blocks,
    unresolved,
):
    enhanced = {
        **graph,
        "kind": "current_atom_model_graph",
        "model": model,
        "constraints": model_constraints,
        "model_contracts": [
            row
            for row in model_constraints
            if row.get("kind") in {"property_constraint", "allowed_literal"}
            and declared(row)
        ],
        "source_constraints": [
            row
            for row in constraints
            if row.get("group") != "instances"
            and non_declaration_property(row)
        ],
        "instance_constraints": [
            row for row in constraints if row.get("group") == "instances"
        ],
        "formal_claim_blocks": [
            block
            for carrier in carriers
            for block in claim_python_blocks(carrier)
        ],
        "claim_diagnostics": unresolved,
    }
    return enhanced
