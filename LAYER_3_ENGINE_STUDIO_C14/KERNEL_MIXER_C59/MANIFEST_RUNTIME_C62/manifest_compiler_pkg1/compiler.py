"""Compile one Project Structure snapshot and, at startup, its Model modules."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_modules
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.native_manifest_model import (
    admit_active_model_records, load_compiled_model, load_native_model, reviewed_model_records,
)
from native_project_selection import resolve_native_project

from .active_model_sources import read_active_model_sources
from .structure_compile import compile_structure


def write_model(directory: Path, control_root: Path) -> str:
    """Write a complete generation into an empty staging directory."""
    ontology = control_root / "LAYER_1_META_ONTOLOGY_C9"
    declarations = None
    if ontology.exists() or ontology.is_symlink():
        declarations = read_active_model_sources(control_root, ontology)
    records, _, fingerprint = (
        reviewed_model_records() if declarations is None else admit_active_model_records(declarations)
    )
    sources = assemble_model_modules(claim for _, _, claim in records)
    package = directory / "anechoic_runtime_model"
    package.mkdir()
    modules = {}
    for filename, source in {"__init__.py": "", **sources}.items():
        data = source.encode("utf-8")
        (package / filename).write_bytes(data)
        modules[filename] = sha256(data).hexdigest()
    (directory / "model.json").write_text(
        json.dumps({"model_sha256": fingerprint, "modules": modules, "declarations": declarations}, sort_keys=True),
        encoding="utf-8",
    )
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
    args = parser.parse_args()
    if args.build_model:
        bootstrap = resolve_native_project(args.project_root, args.control_root,
                                           validate_manifest=load_native_model().validate_manifest)
        if bootstrap.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError("Project Manifest changed. Restart to apply its settings.")
        write_model(args.generation, bootstrap.control_root)
    sys.path.insert(0, str(args.generation))
    model = load_generation_model(args.generation)
    selection = resolve_native_project(args.project_root, args.control_root, validate_manifest=model.validate_manifest,
                                       require_atom_state=model.requires_atom_state,
                                       require_atom_header=model.requires_atom_header)
    if selection.manifest_sha256 != args.project_manifest_sha256:
        raise ValueError("Project Manifest changed. Restart to apply its settings.")
    snapshot = compile_structure(selection, model)
    print(json.dumps(snapshot, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
