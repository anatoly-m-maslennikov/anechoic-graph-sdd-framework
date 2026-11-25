"""Build a pinned Model and Structure generation without activating it."""
import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
from hashlib import sha256
from pathlib import Path, PurePosixPath

ENGINE = Path(__file__).resolve().parents[2]
COMPILER = ("FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR."
            "manifest_compiler_CS1.compiler")
_COMPILER_ENTRY = Path(*COMPILER.split(".")).with_suffix(".py")
_COMPILER_SOURCE_DIRECTORIES = (
    *_COMPILER_ENTRY.parents[:-1],
    Path("FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_MODEL_VALIDATION"),
    Path("FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE"),
    Path("FEATURE_PROGRAMMATIC/FEATURE_TOOLS"),
    Path("FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30"),
)
FIELDS = {"root", "control_root", "manifest_path", "manifest_sha256", "project_prefix"}
_COMPONENT_DIRECTORY = re.compile(r"(?!__).+_C[0-9]+$")
_SPEC_CANDIDATE = re.compile(r"[A-Z]+-S-")
_REVIEWED_MODEL = ENGINE / "FEATURE_PROGRAMMATIC/FEATURE_MODEL/FEATURE_GENERATED_MODEL_C52"
_REVIEWED_CLAIMS = ("native-graph-claims.json", "native-spec-template-claims.json")
_FILE_LIMIT = 64 * 1024 * 1024


def _validate_binding(binding):
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


def validate(binding, output):
    _validate_binding(binding)
    control = Path(binding["root"]) / binding["control_root"]
    if (not output.is_absolute() or output.is_symlink() or not output.is_dir()
            or output.resolve(strict=True) != output or any(output.iterdir())):
        raise ValueError("Output must be an existing empty canonical directory")
    if output == control or control in output.parents:
        raise ValueError("Output must be outside the Project control root")


def _bound_manifest(binding):
    control = Path(binding["root"]) / binding["control_root"]
    manifest = Path(binding["root"]) / binding["manifest_path"]
    if not manifest.exists() and len(PurePosixPath(binding["manifest_path"]).parts) == 1:
        manifest = control / binding["manifest_path"]
    return manifest


def _open_path(path, *, directory=False):
    if any(part == ".env" or part.startswith(".env.") or part.endswith(".env")
           or part in {".ssh", ".aws", ".gnupg"} for part in path.parts):
        raise ValueError("Protected Manifest path")
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in path.parts[1:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        return os.open(path.name, flags | (os.O_DIRECTORY if directory else 0), dir_fd=descriptor)
    finally:
        os.close(descriptor)


def _read_digest(path, limit):
    descriptor = _open_path(path)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError("Invalid Manifest file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read(before.st_size)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    version = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
    if len(data) != before.st_size or version != (after.st_dev, after.st_ino, after.st_size,
                                                   after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError("Project Manifest changed during read")
    return sha256(data).hexdigest(), len(data), version


def verify_pin(binding):
    digest, _, _ = _read_digest(_bound_manifest(binding), _FILE_LIMIT)
    if digest != binding["manifest_sha256"]:
        raise ValueError("Project Manifest binding changed")


def _directory_candidates(directory, consume):
    descriptor = _open_path(directory, directory=True)
    try:
        names = []
        with os.scandir(descriptor) as entries:
            for entry in entries:
                consume()
                if entry.name.endswith((".md", ".py")) or _COMPONENT_DIRECTORY.fullmatch(entry.name):
                    names.append(entry.name)
        return names
    finally:
        os.close(descriptor)


def _compiler_sources(inventory):
    yield ENGINE / _COMPILER_ENTRY
    for relative in _COMPILER_SOURCE_DIRECTORIES:
        directory = ENGINE / relative
        yield from (directory / name for name in inventory(directory)
                    if name.endswith(".py") and not name.startswith("test_"))


def _manifest_candidates(root, control, checkpoint):
    inventories = {}
    remaining = 1_000_000

    def consume():
        nonlocal remaining
        checkpoint()
        remaining -= 1
        if remaining < 0:
            raise ValueError("Manifest input inventory exceeds host ceiling")

    def inventory(directory, *, required=False):
        if directory not in inventories:
            checkpoint()
            try:
                inventories[directory] = _directory_candidates(directory, consume)
            except FileNotFoundError:
                if required:
                    raise
                inventories[directory] = None
        return inventories[directory] or ()

    project = {root / name for name in inventory(root, required=True)
               if name.endswith(".md") and "-PROJECT_MANIFEST--" in name}
    if not project:
        project = {control / name for name in inventory(control, required=True)
                   if Path(name).suffix == ".md"}
    files = set(project)
    pending = [control]
    while pending:
        directory = pending.pop()
        names = inventory(directory, required=True)
        pending.extend(directory / name for name in names if _COMPONENT_DIRECTORY.fullmatch(name))
        for location, carriers in ((directory, names), (directory / "_SPEC", inventory(directory / "_SPEC"))):
            files.update(location / name for name in carriers
                         if name.endswith(".md") and _SPEC_CANDIDATE.match(name))
    ontology = control / "LAYER_1_META_ONTOLOGY_C9"
    for directory in (ontology, ontology / "_SPEC", control / "__PROJECT_CONFIG/CUSTOM_MODEL",
                      control / "002_PROJECT_CONFIG/CUSTOM_MODEL"):
        files.update(directory / name for name in inventory(directory) if name.endswith(".md"))
    files.update(_compiler_sources(inventory))
    files.update(_REVIEWED_MODEL / name for name in _REVIEWED_CLAIMS)
    directories = sorted(str(path) for path, names in inventories.items() if names is not None)
    return project, directories, sorted(files)


def manifest_input_signature(binding, *, watcher_guarded=False) -> str | None:
    """Witness unchanged compiler inputs or leave admission to a fresh compile."""
    deadline = time.monotonic() + 5

    def checkpoint():
        if (not watcher_guarded and time.monotonic() >= deadline
                and os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"):
            raise TimeoutError("Manifest input witness timed out")

    def sample():
        project, directories, files = _manifest_candidates(root, control, checkpoint)
        pinned = _bound_manifest(binding)
        if pinned not in project:
            raise ValueError("Pinned Project Manifest is not a compiler candidate")
        remaining = 1024 * 1024 * 1024
        evidence, versions = [], []
        for path in files:
            checkpoint()
            digest, size, version = _read_digest(path, min(_FILE_LIMIT, remaining))
            if path == pinned and digest != binding["manifest_sha256"]:
                raise ValueError("Project Manifest binding changed")
            remaining -= size
            evidence.append((str(path), digest))
            versions.append(version)
        checkpoint()
        payload = json.dumps((binding, directories, evidence), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode()).hexdigest(), versions

    try:
        _validate_binding(binding)
        root = Path(binding["root"])
        control = root / binding["control_root"]
        before = sample()
        return before[0] if before == sample() else None
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def compile_generation(binding, stage, model_inputs=None):
    env = {key: value for key, value in os.environ.items() if key != "PYTHONHOME"}
    env["PYTHONPATH"] = str(ENGINE)
    model_args = ["--ingested-model"] if model_inputs is not None else ["--build-model"]
    result = subprocess.run(
        [sys.executable, "-B", "-P", "-m", COMPILER, binding["root"], binding["control_root"],
         binding["manifest_sha256"], str(stage), *model_args, "--attest-model"],
        cwd=ENGINE, env=env, input=(json.dumps(model_inputs, default=str).encode() if model_inputs is not None else None),
        capture_output=True, check=False,
    )
    if result.returncode:
        stderr = result.stderr.decode(errors="replace")
        error = ValueError("Manifest compiler failed: " + stderr[-2048:])
        if model_inputs is not None:
            try:
                error.model_diagnostics = json.loads(stderr)["model_diagnostics"]
            except (ValueError, KeyError, TypeError):
                pass
        raise error
    if os.getenv("ANECHOIC_STARTUP_TIMING") == "1" and result.stderr:
        sys.stderr.write(result.stderr[-8192:].decode(errors="replace"))
    artifact = json.loads(result.stdout)
    compiled = artifact["structure"]
    project = compiled["project"]
    if (project["sha256"] != binding["manifest_sha256"]
            or not project["ref"].startswith(binding["project_prefix"] + "-S-")):
        raise ValueError("Compiled Structure has a different Project binding")
    if model_inputs is not None:
        return compiled, artifact["model_descriptor_sha256"], artifact["model_diagnostics"]
    return compiled, artifact["model_descriptor_sha256"]


def build(binding, output, model_inputs=None):
    output = Path(output)
    validate(binding, output)
    verify_pin(binding)
    with tempfile.TemporaryDirectory(prefix=".manifest-build-", dir=output.parent) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        compiled = compile_generation(binding, stage, model_inputs=model_inputs)
        structure, descriptor_hash = compiled[:2]
        raw = json.dumps(structure, sort_keys=True, separators=(",", ":")).encode()
        (stage / "structure.json").write_bytes(raw)
        verify_pin(binding)
        if output.is_symlink() or not output.is_dir() or any(output.iterdir()):
            raise ValueError("Output directory changed during build")
        os.replace(stage, output)
    receipt = {"manifest_sha256": binding["manifest_sha256"], "model_sha256": structure["model_sha256"],
               "model_descriptor_sha256": descriptor_hash, "structure_sha256": sha256(raw).hexdigest()}
    if model_inputs is not None:
        receipt["model_diagnostics"] = compiled[2]
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--ingested-model", action="store_true")
    args = parser.parse_args()
    try:
        request = json.load(sys.stdin)
        if args.ingested_model:
            if not isinstance(request, dict) or set(request) != {"binding", "model_inputs"}:
                raise ValueError("Invalid ingested Model build request")
            result = build(request["binding"], args.output_dir, request["model_inputs"])
        else:
            result = build(request, args.output_dir)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        if args.ingested_model and getattr(error, "model_diagnostics", None):
            print(json.dumps({"model_diagnostics": error.model_diagnostics}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
