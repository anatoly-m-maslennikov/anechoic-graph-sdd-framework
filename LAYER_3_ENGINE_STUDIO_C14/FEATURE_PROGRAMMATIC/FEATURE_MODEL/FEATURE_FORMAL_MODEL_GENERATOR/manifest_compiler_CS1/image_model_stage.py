"""Stage and verify guarded native Model sources for image admission."""

from hashlib import sha256
import json
import os
import re
import selectors
import shutil
from pathlib import Path
import subprocess
import sys
import time
from tempfile import TemporaryDirectory

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import CEILINGS, ReadContext

ROOT = Path(__file__).resolve().parents[5]
ENGINE = "LAYER_3_ENGINE_STUDIO_C14"
ENGINE_ROOT = ROOT / ENGINE
PROGRAMMATIC = ENGINE_ROOT / "FEATURE_PROGRAMMATIC"
ONTOLOGY = "LAYER_1_META_ONTOLOGY_C9"
COMPILE = ("FEATURE_PROGRAMMATIC.FEATURE_MODEL."
           "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.image_model_compile")


MAX_OUTPUT = 4 * 1024 * 1024
_DOCKER_ENVIRONMENT = frozenset({
    "HOME", "PATH", "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG", "XDG_RUNTIME_DIR", "TMPDIR",
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "all_proxy", "no_proxy",
})


def docker_client_environment(*, buildx_config=None):
    environment = {name: value for name, value in os.environ.items() if name in _DOCKER_ENVIRONMENT}
    if buildx_config is not None:
        environment["BUILDX_CONFIG"] = str(buildx_config)
    return environment


def bounded_run(argv, *, cwd, timeout, capture_stdout=True, max_output=MAX_OUTPUT,
                buildx_config=None, report_stderr=False):
    """Read a finite stdout prefix without retaining stderr or build logs."""
    deadline = time.monotonic() + timeout
    environment = docker_client_environment(buildx_config=buildx_config)
    process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE if capture_stdout else subprocess.DEVNULL,
                               stderr=None if report_stderr else subprocess.DEVNULL, shell=False, env=environment)
    selector = None
    output = bytearray()
    try:
        if capture_stdout:
            selector = selectors.DefaultSelector()
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired(argv, timeout)
                for key, _events in selector.select(remaining):
                    chunk = os.read(key.fileobj.fileno(), min(65536, max_output + 1 - len(output)))
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    output.extend(chunk)
                    if len(output) > max_output:
                        raise ValueError("Docker image stdout exceeded its bounded read")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(argv, timeout)
        returncode = process.wait(timeout=remaining)
        return subprocess.CompletedProcess(argv, returncode, output.decode("utf-8"), "")
    finally:
        if selector is not None:
            selector.close()
        if process.stdout is not None:
            process.stdout.close()
        if process.poll() is None:
            try:
                process.kill()
                process.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                pass


def previous_claims(component: Path, image: str, *, timeout: float) -> list[list[str]]:
    if re.fullmatch(r"sha256:[0-9a-f]{64}", image) is None:
        raise ValueError("Previous image must be an immutable image ID")
    deadline = time.monotonic() + timeout
    result = bounded_run(["docker", "image", "inspect", image], cwd=ROOT, timeout=_remaining(deadline))
    if result.returncode:
        raise ValueError("Previous ready image is unavailable")
    [details] = json.loads(result.stdout)
    if (details.get("Id") != image or details.get("Os") != "linux"
            or (details["Config"]["Labels"] or {}).get("org.anechoic.runtime.schema") != "1"):
        raise ValueError("Previous ready image is not an admitted runtime image")

    selector = component.parent / "selector.py"
    if any(set(str(path)) & {",", "\n", "\r"} for path in (component, selector)):
        raise ValueError("Native selector mount path is invalid")
    shutil.copyfile(ENGINE_ROOT / "IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/native_model_selector.py", selector)
    codec_names = ("carrier_read__pub.py", "carrier_syntax__pub.py",
                   "carrier_compat__pub.py", "native_carrier_header__pub.py",
                   "content_records__pub.py", "markdown_content__pub.py", "source_row__pub.py")
    codec_root = PROGRAMMATIC / "FEATURE_TOOLS/ADAPTERS_C30"
    destination = Path("/workspace") / codec_root.relative_to(ROOT)
    codec_mounts = []
    for name in codec_names:
        staged = component.parent / name
        shutil.copyfile(codec_root / name, staged)
        codec_mounts.extend(("--mount", f"type=bind,src={staged},dst={destination / name},readonly"))
    result = bounded_run([
        "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only",
        "--mount", f"type=bind,src={component},dst=/model,readonly",
        "--mount", f"type=bind,src={selector},dst=/selector.py,readonly",
        *codec_mounts,
        "--entrypoint", "/opt/venv/bin/python", image, "/selector.py", "/model",
    ], cwd=ROOT, timeout=_remaining(deadline), report_stderr=True)
    if result.returncode:
        raise ValueError("Previous ready image could not select native Model Claims")
    return json.loads(result.stdout)


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("native model refresh", 0)
    return remaining


def _run(command: list[str], deadline: float) -> str:
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            text=True, timeout=_remaining(deadline), check=True)
    return result.stdout.strip()


def stage_model(project: Path, control: Path, timeout: float, previous: str | None) -> str:
    deadline = time.monotonic() + timeout
    source = control / ONTOLOGY
    compile_command = [sys.executable, "-B", "-P", "-m", COMPILE]
    if not source.exists() and not source.is_symlink():
        return _run(compile_command, deadline)
    reader = ReadContext(roots=[str(control)], limits=dict(CEILINGS))
    temporary = project / ".anechoic_tmp"
    if temporary.is_symlink() or not temporary.is_dir():
        raise ValueError("Native Model staging root is unavailable")
    with TemporaryDirectory(prefix="anechoic-image-model-", dir=temporary) as stage:
        staged = Path(stage) / ONTOLOGY
        staged.mkdir()
        hashes = {}
        for path in reader.inventory_shallow(source):
            raw = reader.read(path)
            (staged / path.name).write_bytes(raw)
            hashes[path.name] = sha256(raw).hexdigest()
        selected = None
        if previous:
            selected = previous_claims(staged, previous, timeout=_remaining(deadline))
        fingerprint = _run([*compile_command, str(staged.parent)], deadline)
        if previous:
            records = json.loads((staged.parent / "model.json").read_text())["declarations"]
            names = [Path(location.rsplit("@", 1)[0]).name for location, _, _ in records]
            if selected != [[name, hashes[name]] for name in sorted(names)]:
                raise ValueError("Previous image selection does not match the current native Model sources")
        if reader.currentness()["state"] != "unchanged":
            raise ValueError("Native Model sources changed during refresh")
        return fingerprint


if __name__ == "__main__":
    print(stage_model(Path(sys.argv[1]), Path(sys.argv[2]), float(sys.argv[3]),
                      sys.argv[4] if len(sys.argv) == 5 else None))
