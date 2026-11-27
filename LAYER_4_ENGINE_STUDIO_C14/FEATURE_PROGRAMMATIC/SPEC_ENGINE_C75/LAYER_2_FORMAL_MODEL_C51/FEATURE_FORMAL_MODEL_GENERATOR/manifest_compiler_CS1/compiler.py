"""Compile one Project Structure snapshot and, at startup, its Model modules."""

from hashlib import sha256
import json
from pathlib import Path

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    admit_active_model_records, assemble_model_modules, compile_native_bindings, load_compiled_model,
    model_module_name, reviewed_model_records,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component

from .active_model_sources import read_active_model_sources


def write_model(directory: Path, control_root: Path, *, verify_lean: bool = False) -> str:
    """Write a complete generation into an empty staging directory."""
    ontology = find_ontology_component(control_root) or control_root / "LAYER_1_META_ONTOLOGY_C9"
    node_locations, node_metadata = {}, {}
    declarations = read_active_model_sources(control_root, ontology, node_locations=node_locations, node_metadata=node_metadata)
    if not ontology.exists() and not ontology.is_symlink():
        if declarations:
            raise ValueError("Custom Model sources require an active C9 Model")
        declarations = None
    return write_model_records(directory, declarations, verify_lean=verify_lean, node_locations=node_locations, node_metadata=node_metadata)


def write_model_records(directory, declarations, *, verify_lean=False, node_locations=None, node_metadata=None):
    records, originals, fingerprint = (
        reviewed_model_records() if declarations is None else admit_active_model_records(declarations)
    )
    bindings = compile_native_bindings(records, originals)
    if verify_lean:
        from .model_lean import verify_model_lean
        verify_model_lean(records, bindings)
    sources = assemble_model_modules((claim for _, _, claim in records), dependency_order=True)
    package = directory / "anechoic_runtime_model"
    package.mkdir()
    modules = {}
    for filename, source in {"__init__.py": "", **sources}.items():
        data = source.encode("utf-8")
        (package / filename).write_bytes(data)
        modules[filename] = sha256(data).hexdigest()
    descriptor = {
        "binding_schema": 1,
        "model_sha256": fingerprint,
        "modules": modules,
        "module_order": list(sources),
        "class_modules": {name: model_module_name(name) for _, declaration in bindings["declarations"]
                          if (name := declaration["arguments"].get("entity_class"))},
        "bindings": bindings,
        "declarations": declarations,
    }
    if node_locations:
        descriptor["node_locations"] = {subject: node_locations[subject] for subject, declaration in bindings["declarations"]
                                        if "entity_class" in declaration["arguments"] and subject in node_locations}
    if node_metadata:
        descriptor.update({key: value for key, value in node_metadata.items() if value})
    (directory / "model.json").write_text(json.dumps(descriptor, sort_keys=True), encoding="utf-8")
    return fingerprint


def load_generation_model(directory: Path):
    descriptor = json.loads((directory / "model.json").read_text(encoding="utf-8"))
    model = load_compiled_model(descriptor["declarations"])
    if model.fingerprint != descriptor["model_sha256"]:
        raise ValueError("The compiled Model differs from its admitted source generation")
    return model


