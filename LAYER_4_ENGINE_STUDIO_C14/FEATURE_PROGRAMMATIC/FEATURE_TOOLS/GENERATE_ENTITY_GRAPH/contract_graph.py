"""Source-bound formal-contract inventory; no CFEL execution or inference."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
    SubjectNotationError as _subject_SubjectNotationError,
    parse_subject_expression as _subject_parse_subject_expression,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import carrier_read_view, matches_named_value
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.cfel_claim_constraints import (
    claim_cfel_blocks,
    claim_fenced_blocks,
    claim_python_blocks,
    claim_prose,
    extract_claim_constraints,
    has_prose_claim,
    section_text,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_common import _has_selection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.current_subject_graph import compose_narrowing_graph
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_targets import _target
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_bindings import (
    _catalog_roots, _conditional_target, _declared_instance_binding, _lexical_term_binding,
    _raw_selector_binding, _root_name, _scope_unit_declaration_contexts,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_common import _source_ref
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_inheritance import (
    _ancestor_property_rows, _ancestor_rows, _inherited_property_rows, _instance_kind,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_relations import _inverse_views, _relation_parts
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.contract_graph_native_properties import _bind_native_property_paths


Record = dict[str, Any]
Candidate = tuple[Record, Mapping[str, Any], str | None, _subject_Path | _subject_RelationChain | None]
_RMED = {"Requirement", "Method", "Evaluation", "Delivery"}
_DECLARATION_FORMS = {"Declaration", "Relation Declaration", "Relation Definition", "Entity Definition"}


def _view(carrier: Mapping[str, Any]) -> Mapping[str, Any]:
    view = carrier.get("read_view")
    if isinstance(view, Mapping):
        return view
    metadata = carrier.get("metadata")
    return carrier_read_view(dict(metadata)) if isinstance(metadata, Mapping) else {}


def _active(carrier: Mapping[str, Any]) -> str | None:
    subjects = carrier.get("subjects")
    if not isinstance(subjects, Mapping):
        return None
    value = carrier_read_view({"subjects": dict(subjects)})["subjects"].get("governs")
    values = value if isinstance(value, list) else [value]
    return values[0] if len(values) == 1 and isinstance(values[0], str) and values[0].strip() else None


def _entry(carrier: Mapping[str, Any], subject: str, target: str, kind: str) -> Record:
    clauses, diagnostics = extract_claim_constraints(carrier)
    source = dict(carrier["source"])
    entry = {
        "source": source, "subject": subject, "target": target, "kind": kind,
        "blocks": claim_fenced_blocks(carrier), "cfel_blocks": claim_cfel_blocks(carrier),
        "clauses": [row for row in clauses if row.get("group") != "instances"],
        "instance_clauses": [row for row in clauses if row.get("group") == "instances"],
        "prose": claim_prose(carrier),
        "prose_claim": has_prose_claim(carrier),
        "claim_scope": section_text(carrier, "Claim Scope"),
        "semantics": section_text(carrier, "Semantics"),
        "details": section_text(carrier, "Details"),
        "diagnostics": [{**row, "source": row.get("source", source)} for row in diagnostics],
    }
    python_blocks = claim_python_blocks(carrier)
    if python_blocks:
        entry["python_blocks"] = python_blocks
    return entry


def _gap(carrier: Mapping[str, Any], message: str, subject: str | None = None) -> Record:
    return {**_entry(carrier, subject or "", "", "unbound"), "message": message}


def _is_declaration(view: Mapping[str, Any]) -> bool:
    return matches_named_value(view.get("content_role"), "Requirement") and any(matches_named_value(view.get("type"), name) for name in _DECLARATION_FORMS)


def _native_class_kind(subject, identity, kind, entry, carrier, gaps):
    native_classes = [clause for clause in entry["clauses"] if clause.get("kind") == "native_class"]
    if native_classes:
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import model_class_target
        if len(native_classes) != 1 or model_class_target(subject, native_classes[0].get("entity_name"), require_namespace=False) != identity:
            gaps.append(_gap(carrier, "Native class requires a matching declared Model Entity Subject.", subject))
            return None
        if kind == "instance" and identity.startswith("Node/") and "//" in identity:
            kind = "primary_node"
            entry["kind"] = kind
    return kind


def _collect_candidates(carriers):
    catalog: dict[tuple[str, str], list[Record]] = defaultdict(list)
    declaration_carriers: list[Record] = []
    candidates: list[Candidate] = []
    gaps: list[Record] = []
    for carrier in carriers:
        try:
            view, subject = _view(carrier), _active(carrier)
        except ValueError as error:
            gaps.append(_gap(carrier, f"Carrier aliases conflict: {error}"))
            continue
        if not any(matches_named_value(view.get("content_role"), name) for name in _RMED):
            continue
        if subject is None:
            gaps.append(_gap(carrier, "Expected exactly one active Subject."))
            continue
        try:
            expression = _subject_parse_subject_expression(subject, subject_profile="approved").expression
        except _subject_SubjectNotationError as error:
            gaps.append(_gap(carrier, str(error), subject))
            continue
        candidates.append((carrier, view, subject, expression))
        if not _is_declaration(view):
            continue
        if expression is None:
            gaps.append(_gap(carrier, "Declaration active Subject is a selector, not one declared target.", subject))
            continue
        target = _target(expression)
        if target is None:
            gaps.append(_gap(carrier, "Declaration active Subject is not a declared Node, Property, Relation, or component.", subject))
            continue
        kind, identity = target
        entry = _entry(carrier, subject, identity, kind)
        kind = _native_class_kind(subject, identity, kind, entry, carrier, gaps)
        if kind is None:
            continue
        catalog[(kind, identity)].append(entry)
        if kind != "relation" and any(
            matches_named_value(view.get("type"), name) for name in {"Declaration", "Entity Definition"}
        ):
            declaration_carriers.append(carrier)

    return catalog, declaration_carriers, candidates, gaps


def _select_binding(subject, expression, catalog, instance_contexts):
    context: Record = {}
    if expression is None:
        selected = _raw_selector_binding(subject, catalog)
        target, binding, context = selected if selected is not None else (None, None, {})
    else:
        target = _target(expression)
        binding = "exact" if target is not None and target in catalog else None
        if binding is None:
            selected = _raw_selector_binding(subject, catalog)
            if selected is not None:
                target, binding, context = selected
        if binding is None:
            selected = _declared_instance_binding(expression, catalog, instance_contexts)
            if selected is not None:
                target, binding, context = selected
        if binding is None:
            conditional = _conditional_target(expression, catalog)
            if conditional is not None:
                target, binding, context = conditional
        if binding is None:
            lexical = _lexical_term_binding(expression, catalog)
            if lexical is not None:
                target, binding, context = lexical
    return target, binding, context


def _bind_shared(candidates, catalog, gaps, outside_scope):
    roots = _catalog_roots(catalog)
    instance_contexts = _scope_unit_declaration_contexts(candidates)
    shared: dict[tuple[str, str], list[Record]] = defaultdict(list)
    for carrier, view, subject, expression in candidates:
        if _is_declaration(view):
            continue
        assert subject is not None
        target, binding, context = _select_binding(subject, expression, catalog, instance_contexts)
        if target is None or binding is None:
            message = ("Active Subject is a complex selection scope; review required."
                       if expression is not None and _has_selection(expression)
                       else "Active Subject has no declared target in this selection.")
            entry = _gap(carrier, message, subject)
            root = _root_name(expression) if expression is not None else "Node"
            if root is not None and root not in roots:
                entry["message"] = "Selected source is outside the declared model scope."
                entry["selection_disposition"] = "outside_model_scope"
                outside_scope.append(entry)
            else:
                gaps.append(entry)
            continue
        kind, identity = target
        entry = _entry(carrier, subject, identity, kind)
        entry["binding"] = binding
        entry["binding_context"] = context
        shared[(kind, identity)].append(entry)

    return shared


def _populate_instance(row, identity, catalog, shared, instance_kind_gaps):
    declared_kind = _instance_kind(identity)
    kind_entries = ([] if declared_kind is None else (
        catalog.get(("primary_node", declared_kind), [])
        or catalog.get(("component", declared_kind), [])
    ))
    kind_shared = ([] if declared_kind is None else (
        shared.get(("primary_node", declared_kind), [])
        or shared.get(("component", declared_kind), [])
    ))
    row["instance_of"] = {
        "target": declared_kind,
        "declaration_refs": sorted(_source_ref(entry["source"]) for entry in kind_entries),
        "effective_source_refs": sorted(_source_ref(entry["source"]) for entry in [*kind_entries, *kind_shared]),
    }
    if declared_kind is None or not kind_entries:
        instance_kind_gaps.append({"instance": identity, "kind": declared_kind})


def _contract_rows(declaration_carriers, catalog, shared):
    narrowing, _ = compose_narrowing_graph(declaration_carriers)
    primary_declarations = {identity: rows for (kind, identity), rows in catalog.items() if kind == "primary_node"}
    ancestors = _ancestor_rows(narrowing, primary_declarations)
    entities, components, relations, namespaces, conflicts, instance_kind_gaps = [], [], [], [], [], []
    for (kind, identity), own in sorted(catalog.items()):
        attached = shared[(kind, identity)]
        if len(own) > 1:
            conflicts.append({"target": identity, "kind": kind, "sources": sorted(_source_ref(row["source"]) for row in own)})
        row = {"target": identity, "kind": kind, "own": own, "shared": attached,
               "shared_sources": sorted(_source_ref(item["source"]) for item in attached)}
        if kind == "primary_node":
            row["transitive_ancestors"] = ancestors.get(identity, [])
            row["inherited_property_declarations"] = _ancestor_property_rows(
                identity, ancestors,
                {target: rows for (target_kind, target), rows in catalog.items() if target_kind == "property"},
            )
            entities.append(row)
        elif kind == "property":
            row["inherited_property_declarations"] = _inherited_property_rows(identity, ancestors, primary_declarations)
            entities.append(row)
        elif kind == "instance":
            _populate_instance(row, identity, catalog, shared, instance_kind_gaps)
            entities.append(row)
        elif kind == "component":
            components.append(row)
        elif kind == "namespace":
            namespaces.append(row)
        else:
            relations.append({**row, **_relation_parts([*own, *attached], identity)})

    return narrowing, entities, components, relations, namespaces, conflicts, instance_kind_gaps


def _finish_graph(catalog, shared, gaps, outside_scope, narrowing, entities, components, relations, namespaces, conflicts, instance_kind_gaps):
    _inverse_views(relations)
    for relation in relations:
        if relation["derivation_links"] and not relation.get("derived_view"):
            relation["derivation_scope"] = "Derivation qualification and endpoint transformation are not structurally interpreted."
    missing_relation_semantics = [
        {"relation": row["target"], "source": entry["source"]}
        for row in relations for entry in row["own"]
        if not (entry["semantics"].strip() or (entry["prose_claim"] and entry["prose"].strip()) or row.get("derived_view"))
    ]
    entries = [item for rows in catalog.values() for item in rows] + [item for rows in shared.values() for item in rows] + gaps + outside_scope
    diagnostics = [item for entry in entries for item in entry["diagnostics"]]
    inheritance_diagnostics = narrowing["diagnostics"]
    coverage = {
        "candidate_sources": len(entries), "bound_sources": len(entries) - len(gaps) - len(outside_scope),
        "declared_entity_targets": len(entities), "declared_component_targets": len(components),
        "declared_relation_targets": len(relations), "shared_sources": sum(len(rows) for rows in shared.values()),
        "fenced_claim_blocks": sum(len(entry["blocks"]) for entry in entries),
        "cfel_blocks": sum(len(entry["cfel_blocks"]) for entry in entries),
        "recognized_clauses": sum(len(entry["clauses"]) for entry in entries),
        "unsupported_clauses": len(diagnostics), "coverage_gaps": len(gaps),
        "outside_model_scope_sources": len(outside_scope),
        "duplicate_declarations": len(conflicts), "missing_relation_semantics": len(missing_relation_semantics),
        "instance_kind_gaps": len(instance_kind_gaps),
        "inheritance_diagnostics": len(inheritance_diagnostics),
    }
    display_incomplete = any((gaps, conflicts, missing_relation_semantics, instance_kind_gaps, inheritance_diagnostics))
    return {
        "kind": "source_bound_formal_contract_graph", "narrowing_tree": narrowing,
        "entities": entities, "components": components, "relations": relations, "namespaces": namespaces,
        "coverage_gaps": gaps, "outside_model_scope": outside_scope, "unresolved": gaps, "conflicts": conflicts,
        "missing_relation_semantics": missing_relation_semantics, "instance_kind_gaps": instance_kind_gaps,
        "diagnostics": diagnostics, "inheritance_diagnostics": inheritance_diagnostics,
        "coverage": coverage,
        "display_coverage": "incomplete" if display_incomplete else "complete",
        "structured_cfel": "partial" if diagnostics else "complete",
        "outcome": "incomplete" if display_incomplete else "complete",
    }


def compose_contract_graph(carriers: list[Record]) -> Record:
    """Group complete selected RMED evidence by a prior declared exact target."""
    catalog, declaration_carriers, candidates, gaps = _collect_candidates(carriers)
    _bind_native_property_paths(catalog, gaps, _target)
    outside_scope: list[Record] = []
    shared = _bind_shared(candidates, catalog, gaps, outside_scope)
    rows = _contract_rows(declaration_carriers, catalog, shared)
    return _finish_graph(catalog, shared, gaps, outside_scope, *rows)
