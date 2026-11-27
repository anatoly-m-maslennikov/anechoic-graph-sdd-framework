"""One current-source test image, never a running Project MCP installation."""


from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

APP = Path("LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP")
CODE_ROOT = Path(__file__).resolve().parents[2]
IMAGE_CLI = ".".join((*APP.parts[1:], "docker", "candidate_image_cli"))
IMAGE_DEADLINES = "ANECHOIC_TEST_IMAGE_DEADLINES"


def image_deadline_mode(environment) -> str:
    return "0" if environment.get(IMAGE_DEADLINES, "0") == "0" else "1"


def image_timeout(seconds: float, environment=None) -> float | None:
    return (
        seconds
        if image_deadline_mode(
            os.environ if environment is None else environment
        )
        == "1"
        else None
    )


def _image_command(root: Path, operation: str, attempt: str, *arguments: str) -> str:
    argv = (
        "uv", "run", "--project", str(CODE_ROOT.parent / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine"), "--locked", "--python", "3.14",
        "--managed-python", "--no-env-file", "python", "-B", "-P", "-m", IMAGE_CLI,
        operation, "--project-root", str(root), "--attempt", attempt, *arguments,
    )
    environment = {
        **os.environ,
        "UV_PROJECT_ENVIRONMENT": str(CODE_ROOT / ".venv-dev"),
        "PYTHONPATH": str(CODE_ROOT),
    }
    environment.pop("PYTHONHOME", None)
    environment.pop("VIRTUAL_ENV", None)
    environment[IMAGE_DEADLINES] = image_deadline_mode(environment)
    result = subprocess.run(
        argv,
        cwd=CODE_ROOT,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        text=True,
        timeout=image_timeout(
            900 if operation == "build" else 120, environment
        ),
        check=True,
    )
    return result.stdout.strip()


def _remove_owned_image(root: Path, image: str, attempt: str) -> None:
    try:
        _image_command(root, "cleanup", attempt, "--image", image)
    except (OSError, subprocess.SubprocessError) as error:
        print(f"Test image cleanup: {image}: {error}", file=sys.stderr)


@contextmanager
def _test_scratch(root: Path):
    parent = root / ".anechoic_tmp/tests/full-suite-integration"
    for component in (root / ".anechoic_tmp", parent.parent, parent):
        if component.is_symlink():
            raise OSError(
                "test scratch must remain inside the selected Project"
            )
    parent.mkdir(parents=True, exist_ok=True)
    if parent.resolve(strict=True) != parent or parent.is_symlink():
        raise OSError("test scratch must remain inside the selected Project")
    with tempfile.TemporaryDirectory(
        prefix="attempt-", dir=parent
    ) as directory:
        yield Path(directory)


def _image_environment(image: str, scratch: Path) -> dict[str, str]:
    return {
        IMAGE_DEADLINES: image_deadline_mode(os.environ),
        "ANECHOIC_IMAGE": image,
        "ANECHOIC_FIRST_CUT_HTTP_IMAGE": image,
        "ANECHOIC_FIRST_CUT_HTTP_SCRATCH": str(scratch),
        "ANECHOIC_DOCKER_QUERY_IMAGE": image,
        "TMPDIR": str(scratch),
        "ANECHOIC_PROJECT_LAUNCHER_DOCKER_E2E": "1",
    }


@contextmanager
def candidate_test_image(root: Path, image: str):
    with _test_scratch(root) as scratch:
        yield _image_environment(image, scratch)


@contextmanager
def current_code_test_image(root: Path, *, use_packaged_assets: bool = False):
    print("Test image START: preparing current source", flush=True)
    with _test_scratch(root) as scratch:
        attempt = uuid.uuid4().hex
        assets = ("--packaged-assets",) if use_packaged_assets else ()
        image = _image_command(
            root, "build", attempt, "--scratch", str(scratch), *assets
        )
        if re.fullmatch(r"sha256:[0-9a-f]{64}", image) is None:
            raise ValueError(
                "Test image build did not return an immutable Docker image ID"
            )
        print(f"Test image FINISH: {image}", flush=True)
        try:
            yield _image_environment(image, scratch)
        finally:
            _remove_owned_image(root, image, attempt)
