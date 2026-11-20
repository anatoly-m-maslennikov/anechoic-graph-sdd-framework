"""Own the two Manifest Runtime processes for one native Project."""

from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
from select import select
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event, Thread

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.source_watcher import SourceWatcher
from project_runtime import bind_native_runtime, owned_temporary_root

_TIMEOUT = 15
_COMPONENT_PATH = re.compile(r"(?!__).+_C[0-9]+$")
_CODE_ROOT = Path(__file__).resolve().parents[3]
_ENGINE = _CODE_ROOT / "LAYER_3_ENGINE_STUDIO_C14"
_PROGRAMMATIC = _ENGINE / "FEATURE_PROGRAMMATIC"


def _command(module):
    return (sys.executable, "-B", "-P", "-m", f"{__package__}.{module}")


def _environment():
    search = os.pathsep.join(map(str, (_CODE_ROOT, _PROGRAMMATIC, _PROGRAMMATIC / "FEATURE_TOOLS",
                                     _ENGINE / "IWE_CONSOLE_C43")))
    return {**os.environ, "PYTHONPATH": search}


@contextmanager
def _host(module, *arguments):
    process = subprocess.Popen(
        (*_command(module), *map(str, arguments)), cwd=_CODE_ROOT, env=_environment(),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    try:
        yield process
    finally:
        try:
            process.stdin.close()
            process.wait(timeout=_TIMEOUT)
        except (BrokenPipeError, subprocess.TimeoutExpired):
            process.kill()
            process.wait()
        finally:
            process.stdout.close()


def _ready(process):
    readable, _, _ = select([process.stdout], [], [], _TIMEOUT)
    if not readable:
        process.kill()
        raise RuntimeError("Manifest Runtime host did not respond")
    if process.stdout.readline() != b"ready\n":
        raise RuntimeError("Manifest Runtime host rejected its generation")


def _compile(selection, generation, *options):
    result = subprocess.run(
        (*_command("manifest_compiler_pkg1.compiler"), str(selection.root),
         selection.control_relative.as_posix(), selection.manifest_sha256, str(generation), *options),
        cwd=_CODE_ROOT, env=_environment(), stdin=subprocess.DEVNULL,
        capture_output=True, timeout=_TIMEOUT, check=False,
    )
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip().splitlines()
        raise RuntimeError(detail[-1] if detail else "Manifest Compiler failed")
    return result.stdout


def _publish(host, active, snapshot):
    active.with_suffix(".pending").write_bytes(snapshot)
    host.stdin.write(b"publish\n")
    host.stdin.flush()
    _ready(host)


def _relevant(relative, control, manifest):
    if relative is None:
        return False
    path = Path(relative)
    return path.is_relative_to(control) and (
        path == manifest or (
            not {"000_draft", "099_archived"}.intersection(path.parts)
            and ("-SPEC-COMPONENT_MANIFEST--" in path.name
                 or "-SPEC-PROJECT_MANIFEST--" in path.name
                 or "-SPEC-PKG--" in path.name
                 or _COMPONENT_PATH.fullmatch(path.name))
        )
    )


def _watch(stop, watcher, selection, active, host):
    manifest = selection.manifest_path.relative_to(selection.root)
    while not stop.is_set():
        changes = watcher.changes(timeout=0.2)
        if stop.is_set() or not any(
            _relevant(change[key], selection.control_relative, manifest)
            for change in changes for key in ("old_path", "new_path")
        ):
            continue
        try:
            _publish(host, active, _compile(selection, active.parent))
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            print(f"Manifest Runtime rebuild failed. {error}", file=sys.stderr, flush=True)


@contextmanager
def run_manifest_runtime(selection):
    """Yield the compiled Model directory and current Structure path."""
    with bind_native_runtime(selection):
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
            snapshot = _compile(selection, generation, "--build-model")
            fingerprint = json.loads(snapshot)["model_sha256"]
            with _host("model_host_pkg2.host", generation, fingerprint) as model_host:
                _ready(model_host)
                with _host("structure_host_pkg3.host", active, fingerprint) as structure_host:
                    _publish(structure_host, active, snapshot)
                    stop = Event()
                    reload_thread = Thread(target=_watch, args=(stop, watcher, selection, active, structure_host))
                    reload_thread.start()
                    try:
                        yield generation, active
                    finally:
                        stop.set()
                        reload_thread.join()
        finally:
            watcher.close()
