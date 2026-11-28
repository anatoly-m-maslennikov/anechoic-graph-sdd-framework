"""Entry points for this Adapter package."""

from .formal_claim__pub import (
    formal_claim as formal_claim,
    iter_formal_claims as iter_formal_claims,
)
from .legacy_relation__pub import (
    emits_instance_inverse as emits_instance_inverse,
)
from .model_catalog__pub import (
    bindings_from_workbench_rows as bindings_from_workbench_rows,
    class_bindings as class_bindings,
)
from .model_class_subject__pub import (
    canonical_model_address as canonical_model_address,
    model_class_target as model_class_target,
    model_declaration_subject as model_declaration_subject,
    simple_model_address as simple_model_address,
)
from .model_ontology_path__pub import (
    is_ontology_model_source as is_ontology_model_source,
    ontology_component_path as ontology_component_path,
)
