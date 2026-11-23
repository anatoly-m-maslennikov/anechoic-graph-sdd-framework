"""Compile Python declarations for the legacy schema projection."""

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_python_model_claim

from .compiler_claim import (
    compile_atom_dependencies_with_check, compile_scope_level_with_check, compiler_model_statements,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim


def compile_python_model_claim(text: str, *, model_class_bindings=None) -> tuple[str, ...]:
    """Read either Python declaration format for the existing schema compilers."""
    native = parse_native_model_claim(text)
    if native is None:
        return parse_python_model_claim(text)
    if native.get("instance_check") is not None:
        if native["instance_check"]["name"] == "dependencies_are_distinct":
            statements, _metadata = compile_atom_dependencies_with_check(native, model_class_bindings=model_class_bindings)
        else:
            statements, _metadata = compile_scope_level_with_check(native)
        return statements
    return compiler_model_statements(native, model_class_bindings=model_class_bindings)


def compile_atom_dependencies_claim_with_check(text: str, *, model_class_bindings=None):
    """Compile the explicit Atom Dependencies consumer's reviewed-callback input."""
    native = parse_native_model_claim(text)
    if native is None:
        raise ValueError("Atom Dependencies requires a native declaration")
    return compile_atom_dependencies_with_check(native, model_class_bindings=model_class_bindings)
