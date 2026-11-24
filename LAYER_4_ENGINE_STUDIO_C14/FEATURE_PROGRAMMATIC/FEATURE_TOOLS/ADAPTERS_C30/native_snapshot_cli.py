"""Capture a pinned native snapshot for the Beta worker CLI."""
import base64
import json
import re
import stat
import sys
from hashlib import sha256
from pathlib import Path, PurePosixPath
from time import monotonic
from types import SimpleNamespace

from .ADAPTERS_C30__pub import CEILINGS, ReadContext
from .carrier_read__pub import parse_carrier
from .native_carrier_placement__pub import ARCHIVE_DIRECTORY, TICKET_DIRECTORY, project_goal_filename
from .native_generation_snapshot import row_summary, snapshot
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


class UnrepresentableCarrierDelta(ValueError):
    pass


class NativeCaptureError(ValueError):
    def __init__(self, capture):
        super().__init__("Native capture failed: " + json.dumps(capture.errors, sort_keys=True))
        self.ingestion_issues = list(capture.ingestion_issues)
        covered = {issue["relative_path"] for issue in self.ingestion_issues}
        self.ingestion_issues.extend(
            {"relative_path": path, "code": "invalid_value", "message": message,
             "atom_ref": None, "related_paths": []}
            for path, message in sorted(capture.errors.items()) if path not in covered
        )


def _check_capture(capture):
    if capture.errors:
        raise NativeCaptureError(capture)


def _capture(binding):
    selection = _selection(binding)
    capture = capture_native(selection)
    _check_capture(capture)
    return capture, _graph_config(selection)


def native_carrier_hashes(binding, *, foreground=False, archive_roots=None, watcher_guarded=False):
    """Hash selected native carriers without parsing them."""
    if foreground and archive_roots is not None:
        raise ValueError("Conflicting native inventory scopes")
    selection = _selection(binding)
    roots = _archive_directories(selection, archive_roots) if archive_roots is not None else None
    return _native_carrier_hashes(selection, foreground=foreground, archive_roots=roots,
                                  watcher_guarded=watcher_guarded)


def _carrier_hashes(capture):
    return {row["source_path"]: row["_source_sha256"] for row in capture.atoms}


def _archive_directories(selection, directories):
    if not isinstance(directories, (list, tuple)):
        raise ValueError("Invalid deferred archive directories")
    installed = selection.control_root / "000_ANECHOIC_framework"
    paths = {selection.root / _relative(path) for path in directories}
    for path in paths:
        if (path == selection.control_root or not path.is_relative_to(selection.control_root)
                or path.is_relative_to(installed) or path.name != ARCHIVE_DIRECTORY):
            raise ValueError("Deferred archive directory is outside the selected native archive trees")
    return tuple(sorted(paths))


def _partition_archived(capture):
    foreground, archived = NativeCapture([], [], {}), NativeCapture([], [], {})
    for row, edge in zip(capture.atoms, capture.containment, strict=True):
        target = archived if row["status_group"] == "Archived" else foreground
        target.atoms.append(row)
        target.containment.append(edge)
    return foreground, archived


def prepare_generation_snapshot(
    binding, *, include_hashes=False, watcher_guarded=False, archive_stage=None, archive_roots=(),
):
    """Capture carriers once and recheck their versions and membership before use.

    A managed caller with continuous watcher coverage can own reconciliation.
    Startup can defer canonical archive directories and retain parsed off-path Archives.
    """
    if archive_stage not in (None, "foreground", "archive") or (archive_roots and archive_stage != "archive"):
        raise ValueError("Invalid generation archive stage")
    selection = _selection(binding)
    reader = ReadContext(roots=[str(selection.root)], limits=dict(CEILINGS))
    deferred = set() if archive_stage == "foreground" else None
    directories = _archive_directories(selection, archive_roots) if archive_stage == "archive" else None
    capture = capture_native(selection, reader=reader, defer_currentness=True,
                             include_content_properties="archive-summary",
                             defer_archives=deferred, archive_roots=directories)
    _check_capture(capture)
    foreground, archived = _partition_archived(capture) if deferred is not None else (capture, None)

    def finish(endpoints):
        result = snapshot(binding, foreground, endpoints)
        if not watcher_guarded:
            reader.started = monotonic()
            if reader.currentness()["state"] != "unchanged":
                raise ValueError("Native Project carriers changed during generation")
        if deferred is not None:
            return (result, _carrier_hashes(foreground),
                    sorted(path.relative_to(selection.root).as_posix() for path in deferred),
                    snapshot(binding, archived, endpoints), _carrier_hashes(archived))
        return (result, _carrier_hashes(foreground)) if include_hashes else result

    return (None if archive_stage == "archive" else _graph_config(selection)), finish


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
            raise UnrepresentableCarrierDelta("Carrier delta contains a non-canonical carrier or Project Manifest")
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
        atoms.append({"reference": row["ref"], "summary": row_summary(row)})
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
