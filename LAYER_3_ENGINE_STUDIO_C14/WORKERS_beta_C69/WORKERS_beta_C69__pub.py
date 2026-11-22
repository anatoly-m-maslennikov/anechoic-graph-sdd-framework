"""Build a transient, pinned Current Atom snapshot from an admitted binding."""
from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import re
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.markdown_content__pub import content_lines

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


def build(binding):
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
    manifest = control / _relative(binding["manifest_path"])
    if control.is_symlink() or not control.is_dir():
        raise ValueError("Invalid control root")
    digest, prefix = binding["manifest_sha256"], binding["project_prefix"]
    if (not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
            or not isinstance(prefix, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix)):
        raise ValueError("Invalid binding identity")
    capture = capture_native(SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                                             manifest_sha256=digest, project_prefix=prefix))
    if capture.errors:
        raise ValueError("Native capture failed: " + json.dumps(capture.errors, sort_keys=True))
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
    return {"manifest_sha256": digest, "atoms": sorted(atoms, key=lambda item: item["reference"])}


def main():
    try:
        result = build(json.load(sys.stdin))
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
