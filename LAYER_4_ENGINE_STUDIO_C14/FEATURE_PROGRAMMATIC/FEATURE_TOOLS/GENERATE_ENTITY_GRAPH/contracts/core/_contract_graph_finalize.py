"""Finalize source-bound contract graph diagnostics."""

from ...contracts.contracts__shared import _inverse_views


def _missing_semantics(relations):
    return [
        {"relation": row["target"], "source": entry["source"]}
        for row in relations
        for entry in row["own"]
        if not (
            entry["semantics"].strip()
            or (entry["prose_claim"] and entry["prose"].strip())
            or row.get("derived_view")
        )
    ]


def _metrics(sources, outputs):
    catalog, shared, gaps, outside_scope, narrowing = sources
    entities, components, relations, conflicts, instance_kind_gaps = outputs
    missing_relation_semantics = _missing_semantics(relations)
    entries = (
        [item for rows in catalog.values() for item in rows]
        + [item for rows in shared.values() for item in rows]
        + gaps
        + outside_scope
    )
    diagnostics = [item for entry in entries for item in entry["diagnostics"]]
    inheritance_diagnostics = narrowing["diagnostics"]
    coverage = {
        "candidate_sources": len(entries),
        "bound_sources": len(entries) - len(gaps) - len(outside_scope),
        "declared_entity_targets": len(entities),
        "declared_component_targets": len(components),
        "declared_relation_targets": len(relations),
        "shared_sources": sum(len(rows) for rows in shared.values()),
        "fenced_claim_blocks": sum(len(entry["blocks"]) for entry in entries),
        "python_blocks": sum(
            len(entry.get("python_blocks", [])) for entry in entries
        ),
        "recognized_clauses": sum(len(entry["clauses"]) for entry in entries),
        "unsupported_clauses": len(diagnostics),
        "coverage_gaps": len(gaps),
        "outside_model_scope_sources": len(outside_scope),
        "duplicate_declarations": len(conflicts),
        "missing_relation_semantics": len(missing_relation_semantics),
        "instance_kind_gaps": len(instance_kind_gaps),
        "inheritance_diagnostics": len(inheritance_diagnostics),
    }
    return (
        missing_relation_semantics,
        diagnostics,
        inheritance_diagnostics,
        coverage,
    )


def _finish_result(graph, unresolved, details, display_incomplete):
    narrowing, entities, components, relations, namespaces = graph
    gaps, outside_scope, conflicts, instance_kind_gaps = unresolved
    (
        missing_relation_semantics,
        diagnostics,
        inheritance_diagnostics,
        coverage,
    ) = details
    return {
        "kind": "source_bound_formal_contract_graph",
        "narrowing_tree": narrowing,
        "entities": entities,
        "components": components,
        "relations": relations,
        "namespaces": namespaces,
        "coverage_gaps": gaps,
        "outside_model_scope": outside_scope,
        "unresolved": gaps,
        "conflicts": conflicts,
        "missing_relation_semantics": missing_relation_semantics,
        "instance_kind_gaps": instance_kind_gaps,
        "diagnostics": diagnostics,
        "inheritance_diagnostics": inheritance_diagnostics,
        "coverage": coverage,
        "display_coverage": "incomplete" if display_incomplete else "complete",
        "structured_claims": "partial" if diagnostics else "complete",
        "outcome": "incomplete" if display_incomplete else "complete",
    }


def _finish_graph(
    catalog,
    shared,
    gaps,
    outside_scope,
    narrowing,
    entities,
    components,
    relations,
    namespaces,
    conflicts,
    instance_kind_gaps,
):
    _inverse_views(relations)
    for relation in relations:
        if relation["derivation_links"] and not relation.get("derived_view"):
            relation["derivation_scope"] = (
                "Derivation qualification and endpoint transformation "
                "are not structurally interpreted."
            )
    details = _metrics(
        (catalog, shared, gaps, outside_scope, narrowing),
        (entities, components, relations, conflicts, instance_kind_gaps),
    )
    missing_relation_semantics, _, inheritance_diagnostics, _ = details
    display_incomplete = any(
        (
            gaps,
            conflicts,
            missing_relation_semantics,
            instance_kind_gaps,
            inheritance_diagnostics,
        )
    )
    return _finish_result(
        (narrowing, entities, components, relations, namespaces),
        (gaps, outside_scope, conflicts, instance_kind_gaps),
        details,
        display_incomplete,
    )
