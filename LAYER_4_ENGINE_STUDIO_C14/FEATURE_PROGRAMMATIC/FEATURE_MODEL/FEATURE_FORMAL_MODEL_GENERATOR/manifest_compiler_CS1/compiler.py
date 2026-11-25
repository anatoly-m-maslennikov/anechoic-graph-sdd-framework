"""Compile one Project Structure snapshot and, at startup, its Model modules."""

import argparse
from hashlib import sha256
import json
import sys
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    admit_active_model_records, assemble_model_modules, compile_native_bindings, load_compiled_model,
    load_native_model, model_module_name, reviewed_model_records,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import resolve_native_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model_ontology_path__pub import find_ontology_component

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model
from .active_model_sources import ModelSourceError, compile_active_model_rows, read_active_model_sources
from .structure_compile__shared import compile_structure


def write_model(directory: Path, control_root: Path) -> str:
    """Write a complete generation into an empty staging directory."""
    ontology = find_ontology_component(control_root) or control_root / "LAYER_1_META_ONTOLOGY_C9"
    declarations = read_active_model_sources(control_root, ontology)
    if not ontology.exists() and not ontology.is_symlink():
        if declarations:
            raise ValueError("Custom Model sources require an active C9 Model")
        declarations = None
    return write_model_records(directory, declarations)


def write_model_records(directory: Path, declarations) -> str:
    """Write a Model generation from admitted source declarations or reviewed fallback."""
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



def build_model_from_rows(directory: Path, rows, *, has_c9: bool) -> str:
    """Compile and admit one Model from an immutable ingestion snapshot."""
    try:
        declarations = compile_active_model_rows(rows, has_c9=has_c9)
        return write_model_records(directory, declarations)
    except ModelSourceError:
        raise
    except (ValueError, TypeError, SyntaxError) as error:
        raise ModelSourceError(None, None, str(error)) from error

def load_generation_model(directory: Path):
    descriptor = json.loads((directory / "model.json").read_text(encoding="utf-8"))
    model = load_compiled_model(descriptor["declarations"])
    if model.fingerprint != descriptor["model_sha256"]:
        raise ValueError("The compiled Model differs from its admitted source generation")
    return model



def compile_ingested(args, inputs):
    """Compile the candidate or reviewed fallback and validate its Structure."""
    from .model_startup import stage_model
    diagnostics = []
    if not isinstance(inputs, dict):
        return {"error": {"code": "model_compile_failed", "message": "Invalid Model snapshot envelope"},
                "model_diagnostics": diagnostics}

    def structure(digest):
        descriptor = json.loads((args.generation / "model.json").read_bytes())
        with open_admitted_model(args.generation, descriptor["model_sha256"], digest) as model:
            selection = resolve_native_project(args.project_root, args.control_root,
                                               validate_manifest=model.validate_manifest,
                                               require_atom_state=model.requires_atom_state,
                                               require_atom_header=model.requires_atom_header,
                                               require_manifest_summary=model.declares_summary("Project Manifest"))
            if selection.manifest_sha256 != args.project_manifest_sha256:
                raise ValueError("Project Manifest changed. Restart to apply its settings.")
            return compile_structure(selection, model)

    try:
        if (args.generation.is_symlink() or not args.generation.is_dir()
                or args.generation.resolve(strict=True) != args.generation or any(args.generation.iterdir())):
            raise ValueError("Model generation must be an empty canonical directory")
        digest = stage_model(args.generation, inputs, inputs.get("accepted_model"), diagnostics)
        try:
            snapshot = structure(digest)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            if diagnostics:
                raise
            digest = stage_model(args.generation, inputs, inputs.get("accepted_model"), diagnostics, fallback=error)
            snapshot = structure(digest)
        return {"structure": snapshot, "model_descriptor_sha256": digest, "model_diagnostics": diagnostics}
    except (OSError, RuntimeError, TypeError, ValueError, SyntaxError) as error:
        return {"error": {"code": "model_compile_failed", "message": str(error)},
                "model_diagnostics": diagnostics}

def _compile_ingested_cli(args):
    try:
        inputs = json.load(sys.stdin)
        result = compile_ingested(args, inputs)
    except (OSError, ValueError, TypeError) as error:
        result = {"error": {"code": "model_compile_failed", "message": str(error)}, "model_diagnostics": []}
    stream = sys.stderr if "error" in result else sys.stdout
    print(json.dumps(result, separators=(",", ":"), sort_keys=True), file=stream)
    if "error" in result:
        raise SystemExit(1)
    return


def _serialize_compiled_model(generation, descriptor, model):
    data = json.loads(descriptor)
    data["ticket_labels"] = model.ticket_labels
    data["module_sources"] = {name: (generation / "anechoic_runtime_model" / name).read_text(encoding="utf-8")
                              for name in data["modules"]}
    if any(sha256(source.encode("utf-8")).hexdigest() != data["modules"][name]
           for name, source in data["module_sources"].items()):
        raise ValueError("Model modules changed during serialization")
    descriptor = json.dumps(data, sort_keys=True).encode("utf-8")
    (generation / "model.json").write_bytes(descriptor)
    digest = sha256(descriptor).hexdigest()
    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("control_root")
    parser.add_argument("project_manifest_sha256")
    parser.add_argument("generation", type=Path)
    parser.add_argument("--ingested-model", action="store_true")
    parser.add_argument("--build-model", action="store_true")
    parser.add_argument("--attest-model", action="store_true")
    parser.add_argument("--model-descriptor-sha256")
    args = parser.parse_args()
    if args.ingested_model:
        _compile_ingested_cli(args)
        return
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
                                           require_atom_header=model.requires_atom_header,
                                           require_manifest_summary=model.declares_summary("Project Manifest"))
        if selection.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError("Project Manifest changed. Restart to apply its settings.")
        snapshot = compile_structure(selection, model)
        if args.build_model:
            digest = _serialize_compiled_model(args.generation, descriptor, model)
    if args.attest_model:
        snapshot = {"structure": snapshot, "model_descriptor_sha256": digest}
    print(json.dumps(snapshot, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
