"""Capture a pinned native snapshot for the Beta worker CLI."""
import base64
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import sys
from types import SimpleNamespace

from .ADAPTERS_C30__pub import CEILINGS, ReadContext
from .carrier_read__pub import parse_carrier
from .native_source_rows__pub import capture_native, check_native_manifest
from .markdown_content__pub import content_lines
from .project_manifest__pub import manifest_inputs

_FIELDS = {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}


def _relative(value, *, direct=False):
    if not isinstance(value, str):
        raise ValueError("Invalid relative path")
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or path.as_posix() != value
            or any(part in {".", ".."} for part in path.parts)
            or (direct and len(path.parts) != 1)):
        raise ValueError("Invalid relative path")
    return path


def _capture(binding):
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
    if not manifest.exists() and len(manifest_relative.parts) == 1:
        manifest = control / manifest_relative
    if manifest.parent != root and not manifest.is_relative_to(control):
        raise ValueError("Invalid Manifest path")
    if control.is_symlink() or not control.is_dir():
        raise ValueError("Invalid control root")
    digest, prefix = binding["manifest_sha256"], binding["project_prefix"]
    if (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not isinstance(prefix, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix)):
        raise ValueError("Invalid binding identity")
    selection = SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                                manifest_sha256=digest, project_prefix=prefix)
    capture = capture_native(selection)
    if capture.errors:
        raise ValueError("Native capture failed: " + json.dumps(capture.errors, sort_keys=True))
    return capture, _graph_config(selection)


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
            from .native_generation_snapshot import snapshot
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
