"""Compile one Project Structure snapshot and, at startup, its Model modules."""
import argparse
from contextlib import redirect_stdout
from io import StringIO
from hashlib import sha256
import json
from pathlib import Path
import sys

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import resolve_native_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import mark_startup_timing
from .LAYER_1_SOURCE_ADAPTERS_C95._package__shared import SpecSnapshot
from .LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import load_native_model
from .LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.manifest_compiler_CS1__shared import compile_ingested_cli, write_model
from .LAYER_2_FORMAL_MODEL_C51.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model
from .LAYER_2_PROJECT_STRUCTURE_C93.LAYER_2_PROJECT_STRUCTURE_C93__shared import compile_structure
from .LAYER_2_PROJECT_STRUCTURE_C93.LAYER_2_PROJECT_STRUCTURE_C93__rows import StructureAdmissionError, compile_structure_rows


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("control_root")
    parser.add_argument("project_manifest_sha256")
    parser.add_argument("generation", type=Path)
    parser.add_argument("--build-model", action="store_true")
    parser.add_argument("--ingested-model", action="store_true")
    parser.add_argument("--verify-lean", action="store_true")
    parser.add_argument("--attest-model", action="store_true")
    parser.add_argument("--model-descriptor-sha256")
    args = parser.parse_args()
    if args.verify_lean and not args.build_model:
        parser.error("--verify-lean requires --build-model")
    if args.ingested_model and (args.build_model or args.verify_lean or args.model_descriptor_sha256 is not None):
        parser.error("--ingested-model cannot be combined with other Model options")
    if not args.build_model and not args.ingested_model and args.model_descriptor_sha256 is None:
        parser.error("Structure refresh requires the admitted Model descriptor hash")
    return args


def _compile_ingested(args):
    raw = json.load(sys.stdin)
    if not isinstance(raw, dict):
        raise ValueError("Invalid ingested Model request")
    snapshot_id = raw.pop("snapshot_id", None)
    alias_issues = raw.pop("structure_alias_issues", [])
    if (not isinstance(alias_issues, list)
            or any(not isinstance(issue, dict) or set(issue) != {'relative_path', 'template'}
                   or any(not isinstance(value, str) or not value for value in issue.values())
                   for issue in alias_issues)):
        raise ValueError("Invalid Structure alias evidence")
    if raw.get("spec_rows") is None:
        if snapshot_id is not None or alias_issues:
            raise ValueError("Spec snapshot identity requires rows")
        sys.stdin = StringIO(json.dumps(raw))
        return compile_ingested_cli(args, compile_structure)
    if not isinstance(snapshot_id, str) or not snapshot_id.strip():
        raise ValueError("Missing Spec snapshot identity")
    snapshot = SpecSnapshot(raw["spec_rows"])
    for model_row in raw["rows"]:
        path = str(Path(args.control_root) / model_row["source_path"])
        row = snapshot.lookup(path)
        if row is None or any(model_row[key] != row[key] for key in ("exact_ref", "metadata", "body")):
            raise ValueError("Model source does not match Spec snapshot " + snapshot_id)
    sys.stdin = StringIO(json.dumps(raw))
    output = StringIO()

    def compile_snapshot(args, model, _rows, manifest_path):
        return compile_structure_rows(args.project_root, args.control_root, args.project_manifest_sha256,
                                      model, snapshot.rows, manifest_path=manifest_path, alias_issues=alias_issues)

    with redirect_stdout(output):
        compile_ingested_cli(args, compile_structure, compile_snapshot=compile_snapshot)
    result = json.loads(output.getvalue())
    result["snapshot_id"] = snapshot_id
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))


def main() -> None:
    args = _parse_args()
    if args.ingested_model:
        _compile_ingested(args)
        return
    if args.build_model:
        bootstrap = resolve_native_project(args.project_root, args.control_root,
                                           validate_manifest=load_native_model().validate_manifest)
        if bootstrap.manifest_sha256 != args.project_manifest_sha256:
            raise ValueError("Project Manifest changed. Restart to apply its settings.")
        if args.verify_lean:
            write_model(args.generation, bootstrap.control_root, verify_lean=True)
        else:
            write_model(args.generation, bootstrap.control_root)
    _compile(args)


def _compile(args):
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
        mark_startup_timing("structure_ready", mode="built")
        if args.build_model:
            digest = _attest_generation(args, descriptor, model)
        mark_startup_timing("model_ready", mode="built" if args.build_model else "reused")
    if args.attest_model:
        snapshot = {"structure": snapshot, "model_descriptor_sha256": digest}
    print(json.dumps(snapshot, separators=(",", ":"), sort_keys=True))


def _attest_generation(args, descriptor, model):
    data = json.loads(descriptor)
    data["ticket_labels"] = model.ticket_labels
    data["module_sources"] = {name: (args.generation / "anechoic_runtime_model" / name).read_text(encoding="utf-8")
                              for name in data["modules"]}
    if any(sha256(source.encode("utf-8")).hexdigest() != data["modules"][name]
           for name, source in data["module_sources"].items()):
        raise ValueError("Model modules changed during serialization")
    descriptor = json.dumps(data, sort_keys=True).encode("utf-8")
    (args.generation / "model.json").write_bytes(descriptor)
    return sha256(descriptor).hexdigest()


if __name__ == "__main__":
    try:
        main()
    except StructureAdmissionError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from error
