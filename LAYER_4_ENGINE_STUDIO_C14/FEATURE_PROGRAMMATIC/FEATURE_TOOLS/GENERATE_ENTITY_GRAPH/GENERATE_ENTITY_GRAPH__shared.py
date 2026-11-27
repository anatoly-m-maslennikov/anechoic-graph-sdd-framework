"""Entity graph family interface."""

from .claim_constraints import _native_constraints, extract_claim_constraints
from .contract_graph import compose_contract_graph
from .contract_graph_render import _clause, render_contract_graph
from .current_subject_graph import (
    compose_current_graph,
    compose_enhanced_current_graph,
    compose_narrowing_graph,
)
from .declaration_relations import resolve_relation_authorities
from .declaration_sources import compose_declaration_catalog
from .declaration_view import render_declarations
from .subject_audit_occurrences import select_model_subjects
from .subject_projection_audits import (
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
        from . import subject_projection_data as provider
    elif name in _READABLE_TREE:
        from . import readable_entity_tree as provider
    elif name in _PROJECTION_VIEWS:
        from . import subject_projection_views as provider
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return (
        provider
        if name in ("readable_entity_tree", "subject_projection_views")
        else getattr(provider, name)
    )
