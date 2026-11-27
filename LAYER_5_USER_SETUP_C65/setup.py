"""Build and start Anechoic for one repository or a repositories folder."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

from settings import Settings, docker_context, select_settings, write_settings
from setup_arguments import parse_arguments as _parse_arguments
from project_init import initialize_project
from codex_install import install_codex


SOURCE = Path(__file__).resolve().parents[1]
RELEASE = Path("LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py")
IMAGE = re.compile(r"sha256:[0-9a-f]{64}")


def parse_arguments(argv: list[str] | None) -> argparse.Namespace:
    return _parse_arguments(argv, __doc__)


def _available(command: str) -> None:
    if shutil.which(command) is None:
        raise ValueError(f"Install {command} and make it available on PATH")


def _preflight(use_codex: bool, env: dict[str, str]) -> None:
    for command in ("git", "uv", "docker"):
        _available(command)
    if use_codex:
        _available("codex")
    label = "OrbStack" if env["DOCKER_CONTEXT"] == "orbstack" else "Docker"
    for command, message in (
        (
            ("docker", "info", "--format", "{{.ServerVersion}}"),
            f"Start {label} and wait for its engine",
        ),
        (
            ("docker", "compose", "version"),
            "Install the Docker Compose plugin",
        ),
    ):
        result = subprocess.run(
            command, capture_output=True, check=False, timeout=20, env=env
        )
        if result.returncode:
            raise ValueError(message)


def _uv(source: Path, script: Path) -> tuple[str, ...]:
    project = source / "LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/release"
    return (
        "uv",
        "run",
        "--project",
        str(project),
        "--locked",
        "--python",
        "3.14",
        "--managed-python",
        "--no-env-file",
        "python",
        "-B",
        "-P",
        str(source / script),
    )


def _run_json(
    source: Path,
    script: Path,
    arguments: tuple[str, ...],
    *,
    action: str,
    timeout: int,
) -> dict:
    command = (*_uv(source, script), *arguments)
    print(f"User Setup: {action}", file=sys.stderr, flush=True)
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("VIRTUAL_ENV", None)
    env["PYTHONPATH"] = str(source / script.parent)
    env["UV_PROJECT_ENVIRONMENT"] = str(
        source / script.parent / ".venv-release"
    )
    result = subprocess.run(
        command,
        cwd=source,
        env=env,
        stdout=subprocess.PIPE,
        text=True,
        check=False,
        timeout=timeout,
    )
    try:
        payload = json.loads(result.stdout)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{action} returned no setup result") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{action} returned an invalid setup result")
    if result.returncode:
        reason = (
            payload.get("condition")
            or payload.get("error_type")
            or f"exit {result.returncode}"
        )
        raise ValueError(f"{action} failed ({reason})")
    return payload


def _initialize(
    source: Path, values: Settings, arguments: argparse.Namespace
) -> bool:
    if not values.single_project:
        if arguments.init_project:
            raise ValueError("--init-project requires a single repository")
        return False
    project = values.folder
    root = subprocess.run(
        ("git", "-C", str(project), "rev-parse", "--show-toplevel"),
        check=False,
        capture_output=True,
        timeout=20,
        text=True,
    )
    if root.returncode or Path(root.stdout.rstrip("\n")) != project:
        raise ValueError("--project must select the Git repository root")
    if any(project.glob("*-PROJECT_MANIFEST--*.md")) or any(
        project.glob("[._]anechoic_*/*-PROJECT_MANIFEST--*.md")
    ):
        return False
    if not arguments.init_project:
        raise ValueError(
            (
                "The repository needs a Project Manifest. Supply "
                "--init-project, --name and --prefix."
            )
        )

    initialize_project(
        source,
        project,
        arguments.name,
        arguments.prefix,
        workbench_storage=values.workbench_storage,
        journal_storage=values.journal_storage,
    )
    return True


def _build_image(source: Path, engine: str, *, timeout: int = 900) -> str:
    build = _run_json(
        source,
        RELEASE,
        (
            "build-image",
            "--engine",
            engine,
            "--project-root",
            str(source),
            "--run-id",
            f"setup-{uuid.uuid4().hex[:12]}",
        ),
        action="build image",
        timeout=timeout,
    )
    image = build.get("image_id")
    if (
        build.get("outcome") != "completed"
        or not isinstance(image, str)
        or not IMAGE.fullmatch(image)
    ):
        raise ValueError(
            "The image build did not return an immutable image ID"
        )
    return image


def _start_image(
    source: Path, engine: str, values: Settings, image: str
) -> None:
    config = values.container
    startup = config.startup_timeout_seconds if config else 420
    readiness = config.readiness_timeout_seconds if config else 420
    launch = _run_json(
        source,
        RELEASE,
        (
            "run-image",
            "--engine",
            engine,
            "--host-settings",
            str(values.path),
            "--image",
            image,
            "--apply",
            "--verify-mcp",
            "--startup-timeout",
            str(startup),
            "--readiness-timeout",
            str(readiness),
        ),
        action="start Docker",
        timeout=startup + readiness + 480,
    )
    if (
        launch.get("ready") is not True
        or launch.get("image") != image
        or launch.get("http_port") != values.port
    ):
        raise ValueError(
            "Docker did not confirm the requested image and HTTP port"
        )


def install(arguments: argparse.Namespace, *, source: Path = SOURCE) -> dict:
    values, create_settings = select_settings(arguments)
    config = values.container
    context = config.docker_context if config and config.docker_context else docker_context(arguments.engine)
    engine = next(
        (name for name in ("orbstack", "docker") if docker_context(name) == context),
        None,
    )
    image = config.image if config else None
    if image is None and config and not config.build_if_missing:
        raise ValueError("Set container.image or enable container.build_if_missing")
    if image is None and engine is None:
        raise ValueError("Set container.image to use Setup with a custom Docker context")
    env = os.environ.copy()
    env.pop("DOCKER_HOST", None)
    env["DOCKER_CONTEXT"] = context
    _preflight(arguments.agent == "codex", env)
    initialized = _initialize(source, values, arguments)
    if image is None:
        timeout = config.build_timeout_seconds + 300 if config else 900
        image = _build_image(source, engine, timeout=timeout)
    if create_settings:
        if config:
            values = replace(values, container=replace(config, image=image))
        write_settings(values)
    _start_image(source, engine or arguments.engine, values, image)
    base = f"http://127.0.0.1:{values.port}"
    endpoint = base + "/anechoic/mcp"
    result = {
        "outcome": "completed",
        "image_id": image,
        "settings": str(values.path),
        "mount": str(values.folder),
        "mode": "project" if values.single_project else "projects",
        "mcp_url": endpoint,
        "health_url": base + "/anechoic/health",
        "project_initialized": initialized,
    }
    if arguments.agent == "codex":
        try:
            result["codex"] = install_codex(source, endpoint)
        except (
            OSError,
            ValueError,
            RuntimeError,
            subprocess.SubprocessError,
        ) as error:
            result.update(
                outcome="failed", failed_step="codex", reason=str(error)
            )
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parse_arguments(argv)
    try:
        result = install(arguments)
    except KeyboardInterrupt:
        print(json.dumps({"outcome": "interrupted"}))
        return 130
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as error:
        print(json.dumps({"outcome": "failed", "reason": str(error)}))
        return 1
    print(json.dumps(result))
    return 0 if result["outcome"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
