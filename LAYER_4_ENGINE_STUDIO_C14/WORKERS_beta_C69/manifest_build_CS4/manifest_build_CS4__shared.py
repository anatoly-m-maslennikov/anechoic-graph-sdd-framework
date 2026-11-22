"""Build a pinned Model and Structure generation without activating it."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import stat
import sys
import tempfile


ENGINE = Path(__file__).resolve().parents[2]
COMPILER = ("FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR."
            "manifest_compiler_CS1.compiler")
FIELDS = {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}


def validate(binding, output):
    if not isinstance(binding, dict) or set(binding) != FIELDS or not all(isinstance(v, str) for v in binding.values()):
        raise ValueError("Invalid binding fields")
    root = Path(binding["root"])
    path = PurePosixPath(binding["manifest_path"])
    control = PurePosixPath(binding["control_root"])
    if (not root.is_absolute() or root.as_posix() != binding["root"] or root.resolve(strict=True) != root
            or control.is_absolute() or len(control.parts) != 1 or control.name != binding["control_root"]
            or control.name == ".."
            or not binding["manifest_path"] or path.is_absolute() or path.as_posix() != binding["manifest_path"]
            or any(part in {".", ".."} for part in path.parts)
            or (len(path.parts) > 1 and path.parts[0] != control.name)
            or not re.fullmatch(r"[0-9a-f]{64}", binding["manifest_sha256"])
            or not re.fullmatch(r"[A-Z][A-Z0-9]*", binding["project_prefix"])):
        raise ValueError("Invalid binding identity or path")
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Output must be an existing empty canonical directory")
    if output == root / binding["control_root"] or root / binding["control_root"] in output.parents:
        raise ValueError("Output must be outside the Project control root")


def verify_pin(binding):
    control = Path(binding["root"]) / binding["control_root"]
    manifest = Path(binding["root"]) / binding["manifest_path"]
    if not manifest.exists() and len(PurePosixPath(binding["manifest_path"]).parts) == 1:
        manifest = control / binding["manifest_path"]
    if any(part == ".env" or part.startswith(".env.") or part.endswith(".env")
           or part in {".ssh", ".aws", ".gnupg"} for part in manifest.parts):
        raise ValueError("Protected Manifest path")
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in manifest.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        file_descriptor = os.open(manifest.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
    finally:
        os.close(descriptor)
    with os.fdopen(file_descriptor, "rb") as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > 64 * 1024 * 1024:
            raise ValueError("Invalid Manifest file")
        data = stream.read(before.st_size)
        after = os.fstat(stream.fileno())
        version = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        if version(before) != version(after):
            raise ValueError("Project Manifest changed during read")
    if sha256(data).hexdigest() != binding["manifest_sha256"]:
        raise ValueError("Project Manifest binding changed")


def compile_generation(binding, stage):
    env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    env["PYTHONPATH"] = str(ENGINE)
    result = subprocess.run(
        [sys.executable, "-B", "-P", "-m", COMPILER, binding["root"], binding["control_root"],
         binding["manifest_sha256"], str(stage), "--build-model", "--attest-model"],
        cwd=ENGINE, env=env, capture_output=True, timeout=90,
    )
    if result.returncode:
        raise ValueError("Manifest compiler failed: " + result.stderr.decode(errors="replace")[-2048:])
    artifact = json.loads(result.stdout)
    compiled = artifact["structure"]
    project = compiled["project"]
    if (project["sha256"] != binding["manifest_sha256"]
            or not project["ref"].startswith(binding["project_prefix"] + "-S-")):
        raise ValueError("Compiled Structure has a different Project binding")
    return compiled, artifact["model_descriptor_sha256"]


def build(binding, output):
    output = Path(output)
    validate(binding, output)
    verify_pin(binding)
    with tempfile.TemporaryDirectory(prefix=".manifest-build-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        structure, descriptor_hash = compile_generation(binding, stage)
        raw = json.dumps(structure, sort_keys=True, separators=(",", ":")).encode()
        (stage / "structure.json").write_bytes(raw)
        verify_pin(binding)
        if output.is_symlink() or not output.is_dir() or any(output.iterdir()):
            raise ValueError("Output directory changed during build")
        os.replace(stage, output)
    return {"manifest_sha256": binding["manifest_sha256"], "model_sha256": structure["model_sha256"],
            "model_descriptor_sha256": descriptor_hash, "structure_sha256": sha256(raw).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        result = build(json.load(sys.stdin), args.output_dir)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
