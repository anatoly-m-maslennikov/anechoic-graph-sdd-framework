"""Run an admitted, bounded native Ticket lifecycle request."""
import base64
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import open_admitted_model
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native, read_structure
from .native_lifecycle import execute_native_lifecycle
from .native_project_selection import resolve_native_project
from .project_runtime import bind_native_runtime

_NAMES = frozenset({"atom_lifecycle_create_draft", "atom_lifecycle_update", "atom_lifecycle_promote_draft", "atom_lifecycle_change_status", "atom_lifecycle_archive"})
_FIELDS = {"binding", "name", "arguments", "generation", "receipt", "stability_sha256"}


def _encode(value):
    if isinstance(value, bytes):
        return {"__bytes_base64__": base64.b64encode(value).decode("ascii")}
    raise TypeError("Unsupported native capture value")


def _task_scope(name, arguments, capture):
    if name == "atom_lifecycle_create_draft" and "newAtom" in arguments:
        value = arguments["newAtom"]
        if not isinstance(value, dict) or value.get("template") not in {"task", "epic"}:
            raise ValueError("Only Task and Epic creation is available")
        return
    field = "sourceCurrent" if name in {"atom_lifecycle_create_draft", "atom_lifecycle_update"} else "target"
    target = arguments.get(field)
    ref = target.get("ref_id") if isinstance(target, dict) else None
    if not isinstance(ref, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*-T-[0-9]+(?:@[1-9][0-9]*-draft)?", ref):
        raise ValueError("Only Task lifecycle targets are available")
    matching = [row for row in capture.atoms if row["ref"] == ref or row["_exact_ref"] == ref]
    if len(matching) != 1 or matching[0]["header_json"].get("context", {}).get("template") != "task":
        raise ValueError("Task lifecycle target is unavailable or ambiguous")
    if name == "atom_lifecycle_archive" and "atom_family" not in matching[0]["header_json"]:
        raise ValueError("Only native Task and Epic archive is available")


def _selection(binding, model, structure):
    if not isinstance(binding, dict) or set(binding) != {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}:
        raise ValueError("Invalid Project binding")
    selection = resolve_native_project(binding["root"], binding["control_root"],
        validate_manifest=model.validate_manifest, require_atom_state=model.requires_atom_state,
        require_atom_header=model.requires_atom_header)
    if (str(selection.root) != binding["root"] or selection.control_relative.as_posix() != binding["control_root"]
            or selection.manifest_path.relative_to(selection.root).as_posix() != binding["manifest_path"]
            or selection.manifest_sha256 != binding["manifest_sha256"] or selection.project_prefix != binding["project_prefix"]):
        raise ValueError("Project binding changed")
    return replace(selection, structure_snapshot=structure)


def run(request):
    if (not isinstance(request, dict) or set(request) != _FIELDS or request["name"] not in _NAMES
            or not isinstance(request["arguments"], dict) or not isinstance(request["receipt"], dict)):
        raise ValueError("Invalid lifecycle request")
    generation = Path(request["generation"])
    if not generation.is_absolute() or generation.is_symlink() or generation.resolve(strict=True) != generation:
        raise ValueError("Invalid generation directory")
    receipt = request["receipt"]
    structure = generation / "structure.json"
    if (sha256(structure.read_bytes()).hexdigest() != receipt["structure_sha256"]
            or receipt["manifest_sha256"] != request["binding"]["manifest_sha256"]):
        raise ValueError("Generation does not match Project binding")
    with open_admitted_model(generation, receipt["model_sha256"], receipt["model_descriptor_sha256"]) as model:
        selection = _selection(request["binding"], model, structure)
        capture = capture_native(selection)
        raw = json.dumps([capture.versions, capture.atoms, capture.containment], sort_keys=True,
                         separators=(",", ":"), default=_encode).encode()
        if capture.errors or sha256(raw).hexdigest() != request["stability_sha256"]:
            raise ValueError("Native Project carriers changed before lifecycle operation")
        _task_scope(request["name"], request["arguments"], capture)
        with bind_native_runtime(selection):
            return execute_native_lifecycle(selection, request["name"], request["arguments"], capture, read_structure,
                previous_capture=capture, ticket_labels=model.ticket_labels, validate_project_spec=model.validate_project_spec)


def main():
    try:
        print(json.dumps(run(json.load(sys.stdin)), ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
