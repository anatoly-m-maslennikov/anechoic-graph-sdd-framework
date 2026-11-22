"""Host one Project's Model and Structure in the calling process."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event, Thread

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_watcher__pub import SourceWatcher
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import ARCHIVE_DIRECTORY, DRAFT_DIRECTORY, READY_DIRECTORY
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.project_temporary__pub import owned_temporary_root

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_generation__pub import open_admitted_model
from ..ORCHESTRATOR_C66.ORCHESTRATOR_C66__shared import Orchestrator
from .process import _BUILDER_PACKAGE, _CODE_ROOT, _command, _environment
from .structure_host_CS3.structure_host_CS3__shared import publish_structure

_TIMEOUT = 15
_COMPONENT_PATH = re.compile(r"(?!__).+_C[0-9]+$")


def _compile(selection, generation, *options, orchestrator):
    kind = "model_build" if "--build-model" in options else "structure_refresh"
    result = orchestrator.run_worker(
        kind,
        (*_command(f"{_BUILDER_PACKAGE}.compiler"), str(selection.root),
         selection.control_relative.as_posix(), selection.manifest_sha256, str(generation), *options),
        cwd=_CODE_ROOT, env=_environment(), timeout=_TIMEOUT,
    )
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip().splitlines()
        raise RuntimeError(detail[-1] if detail else "Manifest Compiler failed")
    return result.stdout


def _relevant(relative, control, manifest):
    if relative is None:
        return False
    path = Path(relative)
    return path.is_relative_to(control) and (
        path == manifest or (
            not {DRAFT_DIRECTORY, READY_DIRECTORY, ARCHIVE_DIRECTORY, "000_draft", "099_archived"}.intersection(path.parts)
            and ("-COMPONENT_MANIFEST--" in path.name
                 or "-PROJECT_MANIFEST--" in path.name
                 or "-COMPONENT_SEED_MANIFEST--" in path.name
                 or _COMPONENT_PATH.fullmatch(path.name))
        )
    )


def _watch(stop, watcher, selection, active, model_sha256, descriptor_sha256, orchestrator):
    manifest = selection.manifest_path.relative_to(selection.root)
    while not stop.is_set():
        changes = watcher.changes(timeout=0.2)
        if stop.is_set() or not any(
            _relevant(change[key], selection.control_relative, manifest)
            for change in changes for key in ("old_path", "new_path")
        ):
            continue
        try:
            snapshot = _compile(selection, active.parent, "--model-descriptor-sha256", descriptor_sha256,
                                orchestrator=orchestrator)
            publish_structure(active, model_sha256, snapshot)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            print(f"Manifest Runtime rebuild failed. {error}", file=sys.stderr, flush=True)


@contextmanager
def run_manifest_runtime(selection, *, orchestrator=None):
    """Yield the compiled Model directory, Structure path, and bound Model."""
    orchestrator = Orchestrator() if orchestrator is None else orchestrator
    parent = owned_temporary_root(selection.root, "manifest_runtime")
    with TemporaryDirectory(dir=parent, prefix="generation-") as directory:
        generation = Path(directory)
        active = generation / "structure.json"
        watcher = SourceWatcher(
            selection.root, selection.control_root,
            poll_bind_mount=os.environ.get("ANECHOIC_RUNTIME_NAMESPACE") == "docker",
        )
        watcher.start()
        try:
            compiled = json.loads(_compile(selection, generation, "--build-model", "--attest-model",
                                           orchestrator=orchestrator))
            descriptor_sha256 = compiled["model_descriptor_sha256"]
            structure = compiled["structure"]
            snapshot = json.dumps(structure, separators=(",", ":"), sort_keys=True).encode()
            fingerprint = structure["model_sha256"]
            with open_admitted_model(generation, fingerprint, descriptor_sha256) as model:
                publish_structure(active, model.fingerprint, snapshot)
                stop = Event()
                reload_thread = Thread(target=_watch,
                                       args=(stop, watcher, selection, active, model.fingerprint,
                                             descriptor_sha256, orchestrator))
                reload_thread.start()
                try:
                    yield generation, active, model
                finally:
                    stop.set()
                    orchestrator.stop()
                    reload_thread.join()
        finally:
            watcher.close()
