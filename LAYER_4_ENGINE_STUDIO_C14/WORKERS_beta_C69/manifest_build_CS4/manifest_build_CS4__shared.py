"""Build a pinned Model and Structure generation without activating it."""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from hashlib import sha256
from pathlib import Path

from .manifest_input import (
    _COMPONENT_DIRECTORY,
    _TIER_ONE_DIRECTORY,
    _bound_manifest,
    _directory_candidates,
    _read_digest,
    _validate_binding,
    validate,
)
from .compiler_output import compile_pinned_generation


ENGINE = Path(__file__).resolve().parents[2]
COMPILER = "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.compile_project__pub"
_COMPILER_ENTRY = Path(*COMPILER.split(".")).with_suffix(".py")
_SPEC_ENGINE = _COMPILER_ENTRY.parent
_FORMAL_MODEL = _SPEC_ENGINE / "LAYER_2_FORMAL_MODEL_C51"
_MODEL_GENERATOR = _FORMAL_MODEL / "FEATURE_FORMAL_MODEL_GENERATOR"
_MODEL_COMPILER = _MODEL_GENERATOR / "manifest_compiler_CS1"
_MODEL_COMPILER_ENTRY = _MODEL_COMPILER / "compiler.py"
_PROJECT_STRUCTURE = _SPEC_ENGINE / "LAYER_2_PROJECT_STRUCTURE_C93"
_STRUCTURE_ENTRY = (
    _PROJECT_STRUCTURE / "LAYER_2_PROJECT_STRUCTURE_C93__shared.py"
)
_COMPILER_SOURCE_DIRECTORIES = (
    *_COMPILER_ENTRY.parents[:-1],
    _SPEC_ENGINE / "LAYER_1_SOURCE_ADAPTERS_C95",
    _MODEL_COMPILER,
    _MODEL_GENERATOR,
    _FORMAL_MODEL,
    _PROJECT_STRUCTURE,
    _FORMAL_MODEL / "FEATURE_MODEL_VALIDATION",
    Path("FEATURE_PROGRAMMATIC/FEATURE_FORMAL_MODEL_ENGINE"),
    Path("FEATURE_PROGRAMMATIC/FEATURE_TOOLS"),
    Path("FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30"),
)
_SPEC_CANDIDATE = re.compile(r"[A-Z]+-S-")
_REVIEWED_MODEL = ENGINE / _FORMAL_MODEL / "FEATURE_GENERATED_MODEL_C52"
_REVIEWED_CLAIMS = (
    "native-graph-claims.json",
    "native-spec-template-claims.json",
)
_FILE_LIMIT = 64 * 1024 * 1024


def verify_pin(binding):
    digest, _, _ = _read_digest(_bound_manifest(binding), _FILE_LIMIT)
    if digest != binding["manifest_sha256"]:
        raise ValueError("Project Manifest binding changed")


def _compiler_sources(inventory):
    yield ENGINE / _COMPILER_ENTRY
    yield ENGINE / _MODEL_COMPILER_ENTRY
    for relative in _COMPILER_SOURCE_DIRECTORIES:
        directory = ENGINE / relative
        yield from (
            directory / name
            for name in inventory(directory)
            if name.endswith(".py") and not name.startswith("test_")
        )


def _compiler_sha256():
    sources = set(
        _compiler_sources(
            lambda directory: _directory_candidates(directory, lambda: None)
        )
    )
    sources.update(_REVIEWED_MODEL / name for name in _REVIEWED_CLAIMS)
    evidence = [
        (
            path.relative_to(ENGINE).as_posix(),
            _read_digest(path, _FILE_LIMIT)[0],
        )
        for path in sorted(sources)
    ]
    return sha256(
        json.dumps(evidence, separators=(",", ":")).encode()
    ).hexdigest()


def _project_manifests(root, control, inventory):
    project = {
        root / name
        for name in inventory(root, required=True)
        if name.endswith(".md") and "-PROJECT_MANIFEST--" in name
    }
    if not project:
        project = {
            control / name
            for name in inventory(control, required=True)
            if Path(name).suffix == ".md"
        }
    return project


def _add_project_model(files, control, inventory):
    for directory in (
        control / "__PROJECT_CONFIG/CUSTOM_MODEL",
        control / "002_PROJECT_CONFIG/CUSTOM_MODEL",
    ):
        files.update(
            directory / name
            for name in inventory(directory)
            if name.endswith(".md")
        )


def _manifest_candidates(root, control, checkpoint):
    inventories, remaining = {}, 1_000_000

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
                inventories[directory] = _directory_candidates(
                    directory, consume
                )
            except FileNotFoundError:
                if required:
                    raise
                inventories[directory] = None
        return inventories[directory] or ()

    project = _project_manifests(root, control, inventory)
    files = set(project)
    pending = [control]
    while pending:
        directory = pending.pop()
        names = inventory(directory, required=True)
        pending.extend(
            directory / name
            for name in names
            if _COMPONENT_DIRECTORY.fullmatch(name)
        )
        _add_manifest_directory(files, directory, names, control, inventory)
    _add_project_model(files, control, inventory)
    files.update(_compiler_sources(inventory))
    files.add(ENGINE / _STRUCTURE_ENTRY)
    files.update(_REVIEWED_MODEL / name for name in _REVIEWED_CLAIMS)
    directories = sorted(
        str(path) for path, names in inventories.items() if names is not None
    )
    return project, directories, sorted(files)


def _add_manifest_directory(files, directory, names, control, inventory):
    for location, carriers in (
        (directory, names),
        (directory / "_SPEC", inventory(directory / "_SPEC")),
    ):
        files.update(
            location / name
            for name in carriers
            if name.endswith(".md") and _SPEC_CANDIDATE.match(name)
        )
    for folder in names:
        if _TIER_ONE_DIRECTORY.fullmatch(
            folder
        ) and not _COMPONENT_DIRECTORY.fullmatch(folder):
            files.update(
                directory / folder / name
                for name in inventory(directory / folder)
                if name.endswith(".md")
            )
    if directory != control and directory.name.endswith("_C9"):
        for location in (
            directory,
            directory / "_SPEC",
            directory / "_DES",
            directory / "_DOM" / "CONT",
        ):
            files.update(
                location / name
                for name in inventory(location)
                if name.endswith(".md")
            )


def _sample_manifest(binding, root, control, checkpoint):
    project, directories, files = _manifest_candidates(
        root, control, checkpoint
    )
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
    payload = json.dumps(
        (binding, directories, evidence),
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode()).hexdigest(), versions


def manifest_input_signature(binding, *, watcher_guarded=False) -> str | None:
    """Witness unchanged inputs before reusing a compiled Manifest."""
    deadline = time.monotonic() + 5

    def checkpoint():
        if (
            not watcher_guarded
            and time.monotonic() >= deadline
            and os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"
        ):
            raise TimeoutError("Manifest input witness timed out")

    try:
        _validate_binding(binding)
        root = Path(binding["root"])
        control = root / binding["control_root"]
        before = _sample_manifest(binding, root, control, checkpoint)
        if watcher_guarded or before == _sample_manifest(
            binding, root, control, checkpoint
        ):
            return before[0]
        return None
    except OSError, RuntimeError, TypeError, ValueError:
        return None


def compile_generation(binding, stage, model_inputs=None):
    return compile_pinned_generation(
        binding,
        stage,
        model_inputs,
        engine=ENGINE,
        compiler=COMPILER,
        compiler_digest=_compiler_sha256,
    )


def build(binding, output, model_inputs=None):
    output = Path(output)
    validate(binding, output)
    offline = model_inputs is None or model_inputs.get("spec_rows") is None
    if offline:
        verify_pin(binding)
    with tempfile.TemporaryDirectory(
        prefix=".manifest-build-", dir=output.parent
    ) as temporary:
        stage = Path(temporary) / "generation"
        stage.mkdir()
        compiled = compile_generation(
            binding, stage, model_inputs=model_inputs
        )
        structure, descriptor_hash = compiled[:2]
        raw = json.dumps(
            structure, sort_keys=True, separators=(",", ":")
        ).encode()
        (stage / "structure.json").write_bytes(raw)
        if offline:
            verify_pin(binding)
        if output.is_symlink() or not output.is_dir() or any(output.iterdir()):
            raise ValueError("Output directory changed during build")
        os.replace(stage, output)
    receipt = {
        "manifest_sha256": binding["manifest_sha256"],
        "model_sha256": structure["model_sha256"],
        "model_descriptor_sha256": descriptor_hash,
        "structure_sha256": sha256(raw).hexdigest(),
    }
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
            if not isinstance(request, dict) or set(request) != {
                "binding",
                "model_inputs",
            }:
                raise ValueError("Invalid ingested Model build request")
            result = build(
                request["binding"], args.output_dir, request["model_inputs"]
            )
        else:
            result = build(request, args.output_dir)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    except (
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
        subprocess.TimeoutExpired,
    ) as error:
        print(str(error), file=sys.stderr)
        if args.ingested_model and getattr(error, "model_diagnostics", None):
            print(json.dumps({"model_diagnostics": error.model_diagnostics}))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
