"""Run an admitted, bounded native Atom lifecycle request."""
from contextlib import ExitStack
from dataclasses import replace
from hashlib import sha256
import json
import re
from pathlib import Path
import sys

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    open_admitted_model, open_serialized_model,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    capture_indexed_lifecycle, capture_native, parse_structure, protected, read_structure,
)
from .native_lifecycle import LIFECYCLE_TOOLS, execute_native_lifecycle
from .native_project_selection import NativeProjectSelection, is_native_control_name, resolve_native_project
from .project_selection import _instance_id, _project_root
from .project_runtime import bind_native_runtime

_FIELDS = {"binding", "name", "arguments", "generation", "receipt"}


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


def _indexed_task(request):
    indexed, arguments = request["indexed_task"], request["arguments"]
    values = arguments.get("newAtom")
    if (request["name"] != "atom_lifecycle_create_draft" or set(arguments) != {"newAtom"}
            or not isinstance(values, dict) or values.get("template") not in ("task", "epic")
            or not isinstance(values.get("container"), dict) or set(values["container"]) != {"component"}
            or not isinstance(indexed, dict) or set(indexed) != {"max_number", "manifest_ref", "component_ids", "ticket_labels"}
            or not isinstance(indexed["max_number"], str) or not re.fullmatch(r"0|[1-9][0-9]*", indexed["max_number"])
            or not isinstance(indexed["manifest_ref"], str) or not indexed["manifest_ref"]
            or any(not isinstance(indexed[key], list) or any(not isinstance(v, str) for v in indexed[key])
                   for key in ("component_ids", "ticket_labels"))):
        raise ValueError("Invalid indexed Task request")
    return indexed


def _indexed_selection(binding, indexed):
    if not isinstance(binding, dict) or set(binding) != {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}:
        raise ValueError("Invalid Project binding")
    root = _project_root(binding["root"])
    relative, manifest = Path(binding["control_root"]), Path(binding["manifest_path"])
    if (str(root) != binding["root"] or relative.as_posix() != binding["control_root"]
            or len(relative.parts) != 1 or not is_native_control_name(relative.name) or protected(relative)
            or manifest.as_posix() != binding["manifest_path"] or manifest.is_absolute() or ".." in manifest.parts
            or manifest.parent not in (Path('.'), relative) or protected(manifest)
            or not isinstance(binding["project_prefix"], str) or not re.fullmatch(r"[A-Z][A-Z0-9]*", binding["project_prefix"])
            or not isinstance(binding["manifest_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", binding["manifest_sha256"])):
        raise ValueError("Invalid Project binding")
    name = relative.name.split("anechoic_", 1)[1]
    return NativeProjectSelection(root, root / relative, relative, _instance_id(root, relative), name,
        binding["project_prefix"], root / manifest, indexed["manifest_ref"], binding["manifest_sha256"])


def _run_indexed(request):
    indexed = _indexed_task(request)
    selection = _indexed_selection(request["binding"], indexed)
    with bind_native_runtime(selection):
        return execute_native_lifecycle(selection, request["name"], request["arguments"], None, read_structure,
            previous_capture=None, ticket_labels=indexed["ticket_labels"], validate_project_spec=None, indexed_task=indexed)


def _run_context(request):
    from .ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import result

    context, binding = request["lifecycle_context"], request["binding"]
    with ExitStack() as stack:
        try:
            structure = parse_structure(json.dumps(context["structure"]).encode("utf-8"))
            if structure.project["sha256"] != binding["manifest_sha256"]:
                raise ValueError("Admitted Structure disagrees with the Project Manifest")
            selection = _indexed_selection(binding, {"manifest_ref": structure.project["ref"]})
            selection = replace(selection, parameters=context["structure"]["project"].get("parameters", {}))
            capture = capture_indexed_lifecycle(selection, context["carriers"], context["max_numbers"],
                                                lenses=context["lenses"],
                                                max_archived_version=context.get("max_archived_version", 0))
            descriptor = context["model"]
            validate = None
            if descriptor is not None:
                if descriptor.get("model_sha256") != structure.model_sha256:
                    raise ValueError("Admitted Model disagrees with the Structure")
                validate = stack.enter_context(open_serialized_model(descriptor)).validate_project_spec
        except (OSError, RuntimeError, TypeError, ValueError, KeyError) as error:
            return result(errors=[{"code": "source_changed", "message": str(error)}])
        with bind_native_runtime(selection):
            return execute_native_lifecycle(selection, request["name"], request["arguments"], capture,
                read_structure, previous_capture=capture, ticket_labels=context["ticket_labels"],
                validate_project_spec=validate, admitted_structure=structure)


def run(request):
    if (not isinstance(request, dict) or set(request) not in (_FIELDS, {"binding", "name", "arguments", "indexed_task"},
            {"binding", "name", "arguments", "lifecycle_context"})
            or request["name"] not in LIFECYCLE_TOOLS or not isinstance(request["arguments"], dict)):
        raise ValueError("Invalid lifecycle request")
    if "indexed_task" in request:
        return _run_indexed(request)
    if "lifecycle_context" in request:
        return _run_context(request)
    if not isinstance(request["receipt"], dict):
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
        capture = capture_native(selection, include_content_properties=False)
        if capture.errors:
            raise ValueError("Native Project capture failed before lifecycle operation")
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
