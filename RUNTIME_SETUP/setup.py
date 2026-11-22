"""Build and start Anechoic for one repository or a repositories folder."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

from RUNTIME_SETUP__shared import Settings, select_settings, write_settings


SOURCE = Path(__file__).resolve().parents[1]
RELEASE = Path("LAYER_5_FRAMEWORK_DELIVERY/release.py")
LAUNCHER = Path(
    "LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/shared_mcp_launcher.py"
)
IMAGE = re.compile(r"sha256:[0-9a-f]{64}")


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True)
    install = commands.add_parser("install", help="build and start the local runtime")
    target = install.add_mutually_exclusive_group()
    target.add_argument("--project", type=Path, help="mount one repository")
    target.add_argument("--projects-root", type=Path, help="mount a directory of repositories")
    install.add_argument("--settings", type=Path, help="host runtime.toml file")
    install.add_argument("--port", type=int, help="loopback HTTP port, defaults to 8092 for new settings")
    install.add_argument("--workbench-storage", choices=("disk", "memory"))
    install.add_argument("--journal-storage", choices=("files", "duckdb"))
    install.add_argument("--init-project", action="store_true", help="initialize a new single Project")
    install.add_argument("--name", help="name for a new Project")
    install.add_argument("--prefix", help="identifier prefix for a new Project")
    agent = install.add_mutually_exclusive_group()
    agent.add_argument("--agent", choices=("codex",))
    agent.add_argument("--codex", action="store_const", const="codex", dest="agent", help="install the Codex integration")
    result = parser.parse_args(argv)
    if result.init_project and not (result.name and result.prefix):
        parser.error("--init-project requires --name and --prefix")
    if not result.init_project and (result.name or result.prefix):
        parser.error("--name and --prefix require --init-project")
    return result


def _available(command: str) -> None:
    if shutil.which(command) is None:
        raise ValueError(f"Install {command} and make it available on PATH")


def _preflight(use_codex: bool) -> None:
    for command in ("git", "uv", "docker"):
        _available(command)
    if use_codex:
        _available("codex")
    for command, message in (
        (("docker", "info", "--format", "{{.ServerVersion}}"), "Start Docker and wait for its engine"),
        (("docker", "compose", "version"), "Install the Docker Compose plugin"),
    ):
        result = subprocess.run(command, capture_output=True, check=False, timeout=20)
        if result.returncode:
            raise ValueError(message)


def _uv(source: Path, script: Path) -> tuple[str, ...]:
    project = source / script.parts[0]
    groups = ("--no-default-groups", "--group", "runtime") if script == LAUNCHER else ()
    return (
        "uv", "run", "--project", str(project), "--locked", "--python", "3.14",
        "--managed-python", "--no-env-file", *groups, "python", "-B", "-P", str(source / script),
    )


def _run_json(source: Path, script: Path, arguments: tuple[str, ...], *, action: str, timeout: int) -> dict:
    command = (*_uv(source, script), *arguments)
    print(f"Runtime Setup: {action}", file=sys.stderr, flush=True)
    env = os.environ.copy()
    env.pop("PYTHONHOME", None)
    env.pop("VIRTUAL_ENV", None)
    env["PYTHONPATH"] = str(source / script.parts[0])
    env["UV_PROJECT_ENVIRONMENT"] = ".venv-release" if script == RELEASE else ".venv-prod"
    result = subprocess.run(command, cwd=source, env=env, stdout=subprocess.PIPE, text=True, check=False, timeout=timeout)
    try:
        payload = json.loads(result.stdout)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{action} returned no setup result") from error
    if not isinstance(payload, dict):
        raise ValueError(f"{action} returned an invalid setup result")
    if result.returncode:
        reason = payload.get("condition") or payload.get("error_type") or f"exit {result.returncode}"
        raise ValueError(f"{action} failed ({reason})")
    return payload


def _initialize(source: Path, values: Settings, arguments: argparse.Namespace) -> bool:
    if not values.single_project:
        if arguments.init_project:
            raise ValueError("--init-project requires a single repository")
        return False
    project = values.folder
    root = subprocess.run(
        ("git", "-C", str(project), "rev-parse", "--show-toplevel"),
        check=False, capture_output=True, timeout=20, text=True,
    )
    if root.returncode or Path(root.stdout.rstrip("\n")) != project:
        raise ValueError("--project must select the Git repository root")
    if any(project.glob("[._]anechoic_*/*-PROJECT_MANIFEST--*.md")):
        return False
    if not arguments.init_project:
        raise ValueError("The repository needs a Project Manifest. Supply --init-project, --name and --prefix.")
    from project_init import initialize_project

    initialize_project(
        source, project, arguments.name, arguments.prefix,
        workbench_storage=values.workbench_storage, journal_storage=values.journal_storage,
    )
    return True


def install(arguments: argparse.Namespace, *, source: Path = SOURCE) -> dict:
    values, create_settings = select_settings(arguments)
    _preflight(arguments.agent == "codex")
    initialized = _initialize(source, values, arguments)
    if create_settings:
        write_settings(values)
    build = _run_json(
        source, RELEASE, ("build-image", "--project-root", str(source), "--run-id", f"setup-{uuid.uuid4().hex[:12]}"),
        action="build image", timeout=900,
    )
    image = build.get("image_id")
    if build.get("outcome") != "completed" or not isinstance(image, str) or not IMAGE.fullmatch(image):
        raise ValueError("The image build did not return an immutable image ID")
    launch = _run_json(
        source, LAUNCHER, ("--host-settings", str(values.path), "--image", image, "--apply", "--verify-mcp",
                           "--startup-timeout", "420", "--readiness-timeout", "420"),
        action="start Docker", timeout=1320,
    )
    if launch.get("ready") is not True or launch.get("image") != image or launch.get("http_port") != values.port:
        raise ValueError("Docker did not confirm the requested image and HTTP port")
    base = f"http://127.0.0.1:{values.port}"
    endpoint = base + "/anechoic/mcp"
    result = {
        "outcome": "completed", "image_id": image, "settings": str(values.path),
        "mount": str(values.folder), "mode": "project" if values.single_project else "projects",
        "mcp_url": endpoint, "health_url": base + "/anechoic/health", "project_initialized": initialized,
    }
    if arguments.agent == "codex":
        from codex_install import install_codex

        try:
            result["codex"] = install_codex(source, endpoint)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
            result.update(outcome="failed", failed_step="codex", reason=str(error))
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = _arguments(argv)
    try:
        result = install(arguments)
    except KeyboardInterrupt:
        print(json.dumps({"outcome": "interrupted"}))
        return 130
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"outcome": "failed", "reason": str(error)}))
        return 1
    print(json.dumps(result))
    return 0 if result["outcome"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
