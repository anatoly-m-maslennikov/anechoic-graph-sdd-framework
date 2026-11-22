"""Build a transient, pinned Current Atom snapshot from an admitted binding."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import subprocess
import tempfile
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
    capture = capture_native(SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                                             manifest_sha256=digest, project_prefix=prefix))
    if capture.errors:
        raise ValueError("Native capture failed: " + json.dumps(capture.errors, sort_keys=True))
    return capture


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



def build(binding):
    return _snapshot(binding, _capture(binding))


def build_generation(binding, output):
    output = Path(output)
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Generation directory must be an existing empty canonical directory")
    before = _capture(binding)
    snapshot = _snapshot(binding, before)
    control = Path(binding["root"]) / binding["control_root"]
    if output == control or control in output.parents:
        raise ValueError("Generation directory must be outside the Project control root")
    identity = output.stat()
    engine = Path(__file__).resolve().parents[1]
    module = "WORKERS_beta_C69.manifest_build_CS4.manifest_build_CS4__pub"
    env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    env["PYTHONPATH"] = str(engine)
    with tempfile.TemporaryDirectory(prefix=".beta-job-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        result = subprocess.run([sys.executable, "-B", "-P", "-m", module, "--output-dir", str(stage)],
                                input=json.dumps(binding), text=True, capture_output=True,
                                cwd=engine, env=env, timeout=120)
        if result.returncode:
            raise ValueError("Manifest build failed: " + result.stderr[-2048:])
        receipt = json.loads(result.stdout)
        fields = {"manifest_sha256", "model_sha256", "model_descriptor_sha256", "structure_sha256"}
        if not isinstance(receipt, dict) or set(receipt) != fields or receipt["manifest_sha256"] != binding["manifest_sha256"]:
            raise ValueError("Invalid Manifest build receipt")
        after = _capture(binding)
        if (before.versions != after.versions or before.atoms != after.atoms
                or before.containment != after.containment):
            raise ValueError("Native Project carriers changed during generation")
        if (output.is_symlink() or not output.is_dir() or output.stat() != identity or any(output.iterdir())):
            raise ValueError("Generation directory changed during build")
        os.replace(stage, output)
    return {"snapshot": snapshot, "receipt": receipt}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generation-dir")
    args = parser.parse_args()
    try:
        binding = json.load(sys.stdin)
        result = build_generation(binding, args.generation_dir) if args.generation_dir else build(binding)
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
