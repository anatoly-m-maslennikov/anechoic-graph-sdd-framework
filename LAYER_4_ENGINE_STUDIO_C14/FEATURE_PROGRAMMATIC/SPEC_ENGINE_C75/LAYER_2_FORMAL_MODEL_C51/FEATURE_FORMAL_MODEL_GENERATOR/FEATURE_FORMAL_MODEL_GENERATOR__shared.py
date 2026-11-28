"""Formal Model Generator family interface."""

from .native._package__shared import (
    admit_active_model_records,
    compile_native_bindings,
    load_compiled_model,
    load_native_model,
    reviewed_model_records,
)
from .native._package__shared import native_manifest_model as native_manifest_model
from .assembly.model_class_assembly import (
    assemble_model_classes,
    assemble_model_modules,
    build_model_class_source,
    model_module_name,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.assembly._manifest_property_validation import (
    _field_name,
)
from .model_declaration_sources import (
    _add_unambiguous_addresses,
    _check_node_axes,
    _check_manifest_property_bearers,
    _check_relation_references,
    _class_property_aliases,
    _merge_constraint_claims,
    _native_claim,
    _native_claim_text,
    relation_axis_values,
    select_model_claims,
    select_model_declarations,
)

__all__ = [
    "admit_active_model_records",
    "compile_native_bindings",
    "load_compiled_model",
    "load_native_model",
    "native_manifest_model",
    "reviewed_model_records",
    "assemble_model_classes",
    "assemble_model_modules",
    "build_model_class_source",
    "model_module_name",
    "_add_unambiguous_addresses",
    "_check_manifest_property_bearers",
    "_check_relation_references",
    "_class_property_aliases",
    "_merge_constraint_claims",
    "relation_axis_values",
    "_native_claim",
    "_native_claim_text",
    "_check_node_axes",
    "_field_name",
    "select_model_claims",
    "select_model_declarations",
]
