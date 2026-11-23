"""Capture a pinned native snapshot for the Beta worker CLI."""
import base64
import json
import re
import stat
import sys
from hashlib import sha256
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

from .ADAPTERS_C30__pub import CEILINGS, ReadContext
from .carrier_read__pub import parse_carrier
from .markdown_content__pub import content_lines
from .native_carrier_placement__pub import TICKET_DIRECTORY, project_goal_filename
from .native_generation_snapshot import snapshot
from .native_source_rows__pub import (
    NativeCapture,
    _native_carrier_hashes,
    capture_native,
    check_native_manifest,
)
from .project_manifest__pub import manifest_inputs

_FIELDS = {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
_TICKET_TREES = {TICKET_DIRECTORY, "001_TICKETS", "__TKT"}
_MAX_TICKET_DELTA_PATHS = 1024


def _relative(value, *, direct=False):
    if not isinstance(value, str):
        raise ValueError("Invalid relative path")
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or path.as_posix() != value
            or any(part in {".", ".."} for part in path.parts)
            or (direct and len(path.parts) != 1)):
        raise ValueError("Invalid relative path")
    return path


def _selection(binding, *, manifest_admitted=False):
    if not isinstance(binding, dict) or set(binding) != _FIELDS:
        raise ValueError("Invalid binding fields")
    root_value = binding["root"]
    if not isinstance(root_value, str):
        raise ValueError("Invalid Project root")
    root = Path(root_value)
    if (not root.is_absolute() or root.as_posix() != root_value or ".." in root.parts
            or root.resolve(strict=True) != root or not root.is_dir()):
        raise ValueError("Invalid Project root")
    control = root / _relative(binding["control_root"], direct=True)
    manifest_relative = _relative(binding["manifest_path"])
    manifest = root / manifest_relative
    if not manifest_admitted and not manifest.exists() and len(manifest_relative.parts) == 1:
        manifest = control / manifest_relative
    if manifest.parent != root and not manifest.is_relative_to(control):
        raise ValueError("Invalid Manifest path")
    if control.is_symlink() or not control.is_dir():
        raise ValueError("Invalid control root")
    digest, prefix = binding["manifest_sha256"], binding["project_prefix"]
    if (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not isinstance(prefix, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix)):
        raise ValueError("Invalid binding identity")
    return SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                           manifest_sha256=digest, project_prefix=prefix)


def _check_capture(capture):
    if capture.errors:
        raise ValueError("Native capture failed: " + json.dumps(capture.errors, sort_keys=True))


def _capture(binding):
    selection = _selection(binding)
    capture = capture_native(selection)
    _check_capture(capture)
    return capture, _graph_config(selection)


def native_carrier_hashes(binding):
    """Hash the raw selected native carrier inventory without parsing carriers."""
    return _native_carrier_hashes(_selection(binding))


def _carrier_hashes(capture):
    return {row["source_path"]: row["_source_sha256"] for row in capture.atoms}


def prepare_generation_snapshot(binding, *, include_hashes=False):
    """Capture carriers once and recheck their versions and membership before use."""
    selection = _selection(binding)
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    capture = capture_native(selection, reader=reader)
    _check_capture(capture)

    def finish(endpoints):
        result = snapshot(binding, capture, endpoints)
        if reader.currentness()["state"] != "unchanged":
            raise ValueError("Native Project carriers changed during generation")
        return (result, _carrier_hashes(capture)) if include_hashes else result

    return _graph_config(selection), finish


def _ticket_paths(selection, paths):
    if not isinstance(paths, (list, tuple)) or not 0 < len(paths) <= _MAX_TICKET_DELTA_PATHS:
        raise ValueError("Invalid Ticket delta path count")
    relatives = {_relative(path) for path in paths}
    for relative in relatives:
        if (len(relative.parts) < 3 or relative.parts[0] != selection.control_root.name
                or relative.parts[1] not in _TICKET_TREES or relative.suffix != ".md"
                or selection.root / relative == selection.manifest_path):
            raise ValueError("Ticket delta path is outside the native Ticket trees")
    return relatives


def _carrier_paths(selection, paths):
    if not isinstance(paths, (list, tuple)) or not 0 < len(paths) <= _MAX_TICKET_DELTA_PATHS:
        raise ValueError("Invalid carrier delta path count")
    relatives = {_relative(path) for path in paths}
    for relative in relatives:
        path = selection.root / relative
        under_control = len(relative.parts) >= 2 and relative.parts[0] == selection.control_root.name
        root_goal = len(relative.parts) == 1 and project_goal_filename(relative.name)
        if (relative.suffix != ".md" or not (under_control or root_goal)
                or path == selection.manifest_path or "-PROJECT_MANIFEST--" in relative.name
                or (under_control and relative.parts[1] == "000_ANECHOIC_framework")):
            raise ValueError("Carrier delta path is outside the selected native carriers")
    return relatives


def _ticket_versions(root, relatives):
    reader = ReadContext(roots=[str(root)], limits=dict(CEILINGS))
    versions = {}
    for relative in relatives:
        path = reader.allowed(root / relative)
        try:
            info = path.lstat()
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Ticket delta path is not a regular file")
        versions[str(path)] = reader.version(info)
    return versions


def _capture_delta(binding, selection, relatives, endpoints, *, include_hashes, ticket_only, manifest_admitted=False):
    versions = _ticket_versions(selection.root, relatives)
    capture = capture_native(selection, previous=NativeCapture([], [], {}), paths=relatives,
                             manifest_admitted=manifest_admitted)
    _check_capture(capture)
    observed = {path: version for path, version in capture.versions.items()
                if path != str(selection.manifest_path)}
    if observed != versions or _ticket_versions(selection.root, relatives) != versions:
        raise ValueError("Ticket delta paths changed during capture")
    ticket = re.compile(rf"{re.escape(selection.project_prefix)}-T-[0-9]+")
    captured_paths = set()
    for row in capture.atoms:
        if ticket_only and not ticket.fullmatch(row["id"]):
            raise ValueError("Ticket delta contains a non-Ticket Atom")
        header = row["header_json"]
        if not ticket_only and (header.get("atom_family") not in {"SPEC", "TKT", "PROJECT_CONFIG"}
                                or header.get("context", {}).get("template") == "project_manifest"):
            raise ValueError("Carrier delta contains a non-canonical carrier or Project Manifest")
        captured_paths.add(str(selection.root / row["source_path"]))
    if captured_paths != versions.keys():
        raise ValueError("Ticket delta rows do not match the changed paths")
    result = {"paths": [[path.parent.as_posix(), path.name] for path in sorted(relatives)],
              "snapshot": snapshot(binding, capture, endpoints)}
    if include_hashes:
        result["carrier_hashes"] = _carrier_hashes(capture)
    return result


def capture_ticket_delta(binding, paths, endpoints, *, include_hashes=False, manifest_admitted=False):
    """Capture only requested Ticket files and retain absent paths for deletion."""
    selection = _selection(binding, manifest_admitted=manifest_admitted)
    return _capture_delta(binding, selection, _ticket_paths(selection, paths), endpoints,
                          include_hashes=include_hashes, ticket_only=True, manifest_admitted=manifest_admitted)


def capture_carrier_delta(binding, paths, endpoints, *, include_hashes=False, manifest_admitted=False):
    """Capture addressed canonical carriers and retain absent paths for deletion."""
    selection = _selection(binding, manifest_admitted=manifest_admitted)
    return _capture_delta(binding, selection, _carrier_paths(selection, paths), endpoints,
                          include_hashes=include_hashes, ticket_only=False, manifest_admitted=manifest_admitted)


def _graph_config(selection):
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    raw = check_native_manifest(reader, selection, None)
    path = selection.manifest_path
    fields, _ = manifest_inputs(path, parse_carrier(raw, path))
    config = fields.get("parameters", {})
    for key in ("runtime", "workbench"):
        if not isinstance(config, dict):
            raise ValueError("Invalid runtime Project settings")
        config = config.get(key, {})
    if not isinstance(config, dict):
        raise ValueError("Invalid import graph Project settings")
    graph = config.get("import_graph", {})
    if graph is not False and not isinstance(graph, dict):
        raise ValueError("Invalid import graph Project settings")
    if reader.currentness()["state"] != "unchanged":
        raise ValueError("Project Manifest changed during capture")
    return None if graph is False else graph


def _snapshot(binding, capture):
    atoms = []
    for row in capture.atoms:
        if row["status_group"] != "Current":
            continue
        records = [item for item in row["content_properties_json"] if item["property_path"] == ["summary"]]
        if len(records) > 1:
            raise ValueError("Duplicate Summary heading")
        summary = ""
        if records:
            record = records[0]
            lines = content_lines(row["_content_bytes"].decode("utf-8"))
            summary = "".join(lines[record["_body_start_line"]:record["_end_line"]]).strip()
        atoms.append({"reference": row["ref"], "summary": summary})
    return {"manifest_sha256": binding["manifest_sha256"], "atoms": sorted(atoms, key=lambda item: item["reference"])}



def _encode(value):
    if isinstance(value, bytes):
        return {"__bytes_base64__": base64.b64encode(value).decode("ascii")}
    raise TypeError("Unsupported native capture value: " + type(value).__name__)


def main():
    try:
        request = json.load(sys.stdin)
        expanded = isinstance(request, dict) and set(request) == {"binding", "endpoints"}
        binding = request["binding"] if expanded else request
        capture, graph_config = _capture(binding)
        if expanded:
            result = snapshot(binding, capture, request["endpoints"])
        else:
            result = _snapshot(binding, capture)
        raw = json.dumps([capture.versions, capture.atoms, capture.containment], sort_keys=True,
                         separators=(",", ":"), default=_encode).encode()
        print(json.dumps({"snapshot": result, "stability_sha256": sha256(raw).hexdigest(),
                          "graph_config": graph_config},
                         ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
