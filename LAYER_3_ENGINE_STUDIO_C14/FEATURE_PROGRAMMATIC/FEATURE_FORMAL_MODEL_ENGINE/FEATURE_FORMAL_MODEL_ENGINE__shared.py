"""Formal Model Engine family interface."""

from .compiler_claim import compile_atom_dependencies_with_check, compile_scope_level_with_check, compiler_model_statements
from .model_catalog import bindings_from_workbench_rows
from .native_component_claim import parse_component_manifest
from .native_model_claim import NativeModelClaimError, parse_native_model_claim, validate_aspect_hierarchy, validate_aspect_instance
from .native_model_lint import has_dataclass_field_contracts, lint_native_model_claim
from .relation_inverse import emits_instance_inverse
from .scope_callback_asset import formal_claim, generated_assets, write_package
from .topic_dependencies import Atom, DEPENDENCIES_CLAIM_SHA256, dependencies_are_distinct, validate_dependencies_claim, verify_packaged_dependencies_check

__all__ = [
    "Atom", "DEPENDENCIES_CLAIM_SHA256", "NativeModelClaimError", "bindings_from_workbench_rows",
    "compile_atom_dependencies_with_check", "compile_scope_level_with_check", "compiler_model_statements",
    "dependencies_are_distinct", "emits_instance_inverse", "formal_claim", "generated_assets",
    "has_dataclass_field_contracts", "lint_native_model_claim", "parse_component_manifest",
    "parse_native_model_claim", "validate_aspect_hierarchy", "validate_aspect_instance",
    "validate_dependencies_claim", "verify_packaged_dependencies_check", "write_package",
]
