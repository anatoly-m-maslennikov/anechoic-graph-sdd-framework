"""Source-bound Python formal-contract inventory."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from typing import Any

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.notation.notation__shared import (
    Path as _subject_Path,
    RelationChain as _subject_RelationChain,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    carrier_read_view as carrier_read_view,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.carriers__shared import (
    matches_named_value as matches_named_value,
)
from ...claims.claims__shared import (
    extract_claim_constraints as extract_claim_constraints,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claims.primitives.primitives__shared import (
    claim_fenced_blocks,  # noqa: F401
    claim_python_blocks,  # noqa: F401
    claim_prose,  # noqa: F401
    has_prose_claim,  # noqa: F401
    section_text,  # noqa: F401
)
from ...subjects.subjects__shared import (
    _has_selection,
)
from ...subjects.current.current__shared import (
    compose_narrowing_graph as compose_narrowing_graph,
)
from ...contracts.contracts__shared import (
    _declaration_target as _declaration_target,
    _target,
)
from ...contracts.contracts__shared import (
    _catalog_roots,
    _conditional_target,
    _declared_instance_binding,
    _lexical_term_binding,
    _raw_selector_binding,
    _root_name,
    _scope_unit_declaration_contexts,
)
from ...contracts.contracts__shared import (
    _source_ref as _source_ref,
)
from .contract_graph_inheritance import (
    _ancestor_property_rows as _ancestor_property_rows,
    _ancestor_rows as _ancestor_rows,
    _inherited_property_rows as _inherited_property_rows,
    _instance_kind as _instance_kind,
)
from ...contracts.contracts__shared import (
    _inverse_views as _inverse_views,
    _relation_parts as _relation_parts,
)
from .contract_graph_native_properties import (
    _bind_native_property_paths,
)


from ._contract_graph_candidates import (
    _RMED as _RMED,
    _DECLARATION_FORMS as _DECLARATION_FORMS,
    _view as _view,
    _active as _active,
    _entry as _entry,
    _gap as _gap,
    _is_declaration as _is_declaration,
    _native_class_kind as _native_class_kind,
    _collect_candidates as _collect_candidates,
)


from ._contract_graph_finalize import _finish_graph as _finish_graph


from ._contract_graph_assembly import (
    _populate_instance as _populate_instance,
    _classify_row as _classify_row,
    _contract_rows as _contract_rows,
)


Record = dict[str, Any]
Candidate = tuple[
    Record,
    Mapping[str, Any],
    str | None,
    _subject_Path | _subject_RelationChain | None,
]


def _select_binding(subject, expression, catalog, instance_contexts):
    context: Record = {}
    if expression is None:
        selected = _raw_selector_binding(subject, catalog)
        target, binding, context = (
            selected if selected is not None else (None, None, {})
        )
    else:
        target = _target(expression)
        binding = "exact" if target is not None and target in catalog else None
        if binding is None:
            selected = _raw_selector_binding(subject, catalog)
            if selected is not None:
                target, binding, context = selected
        if binding is None:
            selected = _declared_instance_binding(
                expression, catalog, instance_contexts
            )
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
        target, binding, context = _select_binding(
            subject, expression, catalog, instance_contexts
        )
        if target is None or binding is None:
            message = (
                "Active Subject is a complex selection scope; review required."
                if expression is not None and _has_selection(expression)
                else "Active Subject has no declared target in this selection."
            )
            entry = _gap(carrier, message, subject)
            root = _root_name(expression) if expression is not None else "Node"
            if root is not None and root not in roots:
                entry["message"] = (
                    "Selected source is outside the declared model scope."
                )
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


def compose_contract_graph(carriers: list[Record]) -> Record:
    """Group complete selected RMED evidence by a prior declared exact \
target."""
    catalog, declaration_carriers, candidates, gaps = _collect_candidates(
        carriers
    )
    _bind_native_property_paths(catalog, gaps, _target)
    outside_scope: list[Record] = []
    shared = _bind_shared(candidates, catalog, gaps, outside_scope)
    rows = _contract_rows(declaration_carriers, catalog, shared)
    return _finish_graph(catalog, shared, gaps, outside_scope, *rows)
