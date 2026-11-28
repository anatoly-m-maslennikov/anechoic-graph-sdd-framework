"""Entity graph family interface."""

from .claims.claims__shared import (
    _native_constraints,
    extract_claim_constraints,
)
from .contracts.core.core__shared import compose_contract_graph
from .contract_graph_render import _clause, render_contract_graph
from .subjects.current.current__shared import (
    compose_current_graph,
    compose_enhanced_current_graph,
    compose_narrowing_graph,
)
from .declarations.declarations__shared import resolve_relation_authorities
from .declarations.declarations__shared import compose_declaration_catalog
from .declarations.views.views__shared import render_declarations
from .subjects.audit.audit__shared import select_model_subjects
from .subjects.audit.audit__shared import (
    build_subject_audits,
    render_subject_audit,
)

_PROJECTION_DATA = ("_rule_groups", "build_subject_projection_data")
_READABLE_TREE = ("readable_entity_tree", "render_inherency", "render_model")
_PROJECTION_VIEWS = (
    "_claims",
    "_formal_fence",
    "render_primary_projection",
    "subject_projection_views",
)

__all__ = [
    "_native_constraints",
    "compose_contract_graph",
    "compose_current_graph",
    "compose_enhanced_current_graph",
    "compose_narrowing_graph",
    "extract_claim_constraints",
    "render_contract_graph",
    "build_subject_audits",
    "compose_declaration_catalog",
    "render_declarations",
    "render_subject_audit",
    "resolve_relation_authorities",
    "select_model_subjects",
    "_clause",
    *_PROJECTION_DATA,
    *_READABLE_TREE,
    *_PROJECTION_VIEWS,
]


def __getattr__(name):
    if name in _PROJECTION_DATA:
        from .subjects.projection import projection__shared as provider
    elif name in _READABLE_TREE:
        from .declarations.views.views__shared import (
            readable_entity_tree as provider,
        )
    elif name in _PROJECTION_VIEWS:
        from .subjects.views.views__shared import (
            subject_projection_views as provider,
        )
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return (
        provider
        if name in ("readable_entity_tree", "subject_projection_views")
        else getattr(provider, name)
    )
