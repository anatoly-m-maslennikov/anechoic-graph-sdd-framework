"""Current subject selection and relation primitives."""

from .current_subject_common import (
    Record as Record,
    _NAMESPACE_ROOTS as _NAMESPACE_ROOTS,
    _has_selection as _has_selection,
    _identifier as _identifier,
    _is_declaration as _is_declaration,
    _is_relation_definition as _is_relation_definition,
    _model_target as _model_target,
    _relation_definition_target as _relation_definition_target,
    _target_kind as _target_kind,
    _view as _view,
    namespace_local_expression as namespace_local_expression,
    subject_facts as subject_facts,
)
from .current_subject_formal import (
    _formal_relations as _formal_relations,
    _source_sets as _source_sets,
)
from .current_subject_relation_paths import (
    NarrowingRelationPaths as NarrowingRelationPaths,
)
