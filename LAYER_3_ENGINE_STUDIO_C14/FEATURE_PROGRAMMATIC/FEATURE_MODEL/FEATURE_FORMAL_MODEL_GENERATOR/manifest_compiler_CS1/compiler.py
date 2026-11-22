"""Compile one Project Structure snapshot and, at startup, its Model modules."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_modules, model_module_name
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import (
    admit_active_model_records, compile_native_bindings, load_compiled_model, load_native_model, reviewed_model_records,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__pub import resolve_native_project

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_generation__pub import open_admitted_model
from .active_model_sources import read_active_model_sources
from .structure_compile__shared import compile_structure


def write_model(directory: Path, control_root: Path) -> str:
    """Write a complete generation into an empty staging directory."""
    ontology = control_root / "LAYER_1_META_ONTOLOGY_C9"
    declarations = read_active_model_sources(control_root, ontology)
    if not ontology.exists() and not ontology.is_symlink():
        if declarations:
            raise ValueError("Custom Model sources require an active C9 Model")
        declarations = None
    records, originals, fingerprint = (
        reviewed_model_records() if declarations is None else admit_active_model_records(declarations)
    )
    bindings = compile_native_bindings(records, originals)
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
    (directory / "model.json").write_text(json.dumps(descriptor, sort_keys=True), encoding="utf-8")
    return fingerprint


def load_generation_model(directory: Path):
    descriptor = json.loads((directory / "model.json").read_text(encoding="utf-8"))
    model = load_compiled_model(descriptor["declarations"])
    if model.fingerprint != descriptor["model_sha256"]:
        raise ValueError("The compiled Model differs from its admitted source generation")
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("control_root")
    parser.add_argument("project_manifest_sha256")
    parser.add_argument("generation", type=Path)
    parser.add_argument("--build-model", action="store_true")
    parser.add_argument("--attest-model", action="store_true")
    parser.add_argument("--model-descriptor-sha256")
    args = parser.parse_args()
    if not args.build_model and args.model_descriptor_sha256 is None:
        parser.error("Structure refresh requires the admitted Model descriptor hash")
    if args.build_model:
        bootstrap = resolve_native_project(args.project_root, args.control_root,
                                           validate_manifest=load_native_model().validate_manifest)
        if bootstrap.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError("Project Manifest changed. Restart to apply its settings.")
        write_model(args.generation, bootstrap.control_root)
    descriptor = (args.generation / "model.json").read_bytes()
    digest = sha256(descriptor).hexdigest()
    if args.model_descriptor_sha256 is not None and digest != args.model_descriptor_sha256:
        raise ValueError("model descriptor hash mismatch")
    fingerprint = json.loads(descriptor)["model_sha256"]
    with open_admitted_model(args.generation, fingerprint, digest) as model:
        selection = resolve_native_project(args.project_root, args.control_root, validate_manifest=model.validate_manifest,
                                           require_atom_state=model.requires_atom_state,
                                           require_atom_header=model.requires_atom_header)
        if selection.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError("Project Manifest changed. Restart to apply its settings.")
        snapshot = compile_structure(selection, model)
    if args.attest_model:
        snapshot = {"structure": snapshot, "model_descriptor_sha256": digest}
    print(json.dumps(snapshot, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
