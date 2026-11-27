"""Run the Project release commands directly from the host."""


from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stdout
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from time import time
from uuid import uuid4

sys.dont_write_bytecode = True
REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPOSITORY / "LAYER_4_ENGINE_STUDIO_C14"))


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation in ("local", "public", "build-image", "verify-image", "prepare-local"):
        command = commands.add_parser(operation)
        command.add_argument("--project-root", type=Path, default=REPOSITORY)
        command.add_argument("--run-id", required=operation != "local")
        if operation in ("local", "build-image", "verify-image"):
            _engine_argument(command)
        if operation == "public":
            command.add_argument("--base", default="origin/main", help="PR base Git ref")
            command.add_argument("--head", default="amm/dev", help="PR head Git ref")
            command.add_argument(
                "--content-draft", type=Path, help="UTF-8 JSON with the reviewed change entries"
            )
        elif operation == "prepare-local":
            command.add_argument("--base", required=True, help="exact base commit")
            command.add_argument("--changed-path", action="append", required=True, dest="changed_paths",
                                 metavar="PATH", help="literal repository-relative file addition, edit, or deletion")
            command.add_argument("--port", required=True, type=int, help="isolated loopback MCP port")
        elif operation == "local":
            _local_arguments(command)
    run_image = commands.add_parser("run-image")
    _engine_argument(run_image)
    location = run_image.add_mutually_exclusive_group()
    location.add_argument("--host-settings", type=Path)
    location.add_argument("--mounted-folder", type=Path)
    run_image.add_argument("--image")
    run_image.add_argument("--apply", action="store_true")
    run_image.add_argument("--verify-mcp", action="store_true")
    run_image.add_argument("--startup-timeout", type=int)
    run_image.add_argument("--readiness-timeout", type=int)
    arguments = parser.parse_args(argv)
    if (arguments.operation in ("local", "verify-image") and arguments.run_id is not None
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", arguments.run_id) is None):
        parser.error("--run-id must contain only letters, digits, dots, underscores, or hyphens")
    if arguments.operation == "local":
        _validate_local_arguments(parser, arguments)
    return arguments


def _engine_argument(command):
    command.add_argument("--engine", choices=("orbstack", "docker"),
                         default="orbstack" if sys.platform == "darwin" else "docker",
                         help="container engine (default: %(default)s)")


@contextmanager
def _engine_environment(engine):
    if engine is None:
        yield
        return
    saved = {key: os.environ.get(key) for key in ("DOCKER_CONTEXT", "DOCKER_HOST")}
    docker_context = "desktop-linux" if sys.platform == "darwin" else "default"
    os.environ["DOCKER_CONTEXT"] = "orbstack" if engine == "orbstack" else docker_context
    os.environ.pop("DOCKER_HOST", None)
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _local_arguments(command):
    mode = command.add_mutually_exclusive_group()
    mode.add_argument("--resume", action="store_true", help="continue the recorded Local Release")
    mode.add_argument("--continue", dest="continue_run", action="store_true", help="continue from the target journal")
    mode.add_argument("--abort", action="store_true", help="request a stop at a safe checkpoint")
    mode.add_argument("--status", action="store_true", help="read the recorded Local Release progress")
    mode.add_argument("--prepare-environment", action="store_true", help="provision and verify the checkout's test dependencies")
    command.add_argument("--target-project-root", type=Path, help="Project receiving the verified release")
    command.add_argument("--source-revision", help="exact Git commit for a separate release source")
    command.add_argument("--suite", choices=("full", "fast"), help="Functional suite (default: full)")
    command.add_argument(
        "--base", help="exact base commit for a scoped release"
    )
    command.add_argument("--changed-path", action="append", dest="changed_paths", metavar="PATH",
                         help="literal file overlay for a scoped release")
    command.add_argument(
        "--image-mode", choices=("refresh", "existing"),
        help="candidate image mode; both use the checked-in build assets",
    )
    command.add_argument(
        "--test-module", action="append", dest="test_modules", metavar="PATH",
        help="repeatable relative source test module for focused validation",
    )


def _validate_local_arguments(parser, arguments):
    target, revision = arguments.target_project_root, arguments.source_revision
    if arguments.resume and arguments.run_id is None:
        parser.error("--resume requires --run-id")
    if arguments.base is not None or arguments.changed_paths:
        if (not arguments.base or not arguments.changed_paths or target is not None or revision is not None
                or any((arguments.resume, arguments.status, arguments.abort,
                        arguments.continue_run, arguments.prepare_environment))):
            parser.error("--base and --changed-path must be used together to start a scoped Local Release")
    if arguments.continue_run or arguments.abort:
        if any(value is not None for value in (target, revision, arguments.image_mode, arguments.test_modules, arguments.suite)):
            parser.error("--continue and --abort use the recorded release inputs")
        return
    if arguments.run_id is None and not arguments.status:
        arguments.run_id = uuid4().hex[:12]
    if (arguments.status or arguments.prepare_environment) and any(
        value is not None for value in (target, revision, arguments.image_mode, arguments.test_modules, arguments.suite)
    ):
        parser.error("--status and --prepare-environment each take a single --project-root")
    if (target is None) != (revision is None):
        parser.error("--target-project-root and --source-revision must be supplied together")
    if revision is not None and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision) is None:
        parser.error("--source-revision must be an exact lowercase Git commit SHA")


def _read_draft(path: Path | None) -> dict[str, object] | None:
    if path is None:
        return None
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(descriptor, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise ValueError("content-draft-file-invalid")
        payload = source.read(1_048_577)
    if len(payload) > 1_048_576:
        raise ValueError("content-draft-file-too-large")
    draft = json.loads(payload.decode("utf-8"))
    if not isinstance(draft, dict):
        raise ValueError("content-draft-object-required")
    return draft


def _invoke(arguments: argparse.Namespace) -> dict[str, object]:
    if arguments.operation == "run-image":
        return _run_image(arguments)
    try:
        root = _project_root(arguments.project_root)
    except (OSError, ValueError):
        if arguments.operation in ("local", "verify-image"):
            return _invalid_selection(arguments.run_id)
        raise
    pattern = (
        r"[A-Za-z0-9][A-Za-z0-9._:-]*"
        if arguments.operation == "public"
        else r"[A-Za-z0-9][A-Za-z0-9._-]*"
    )
    if arguments.run_id is not None and re.fullmatch(pattern, arguments.run_id) is None:
        raise ValueError("release-run-id-invalid")
    if arguments.operation == "prepare-local":
        from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import prepare_local

        try:
            return prepare_local(root, run_id=arguments.run_id, base=arguments.base,
                                 changed_paths=arguments.changed_paths, port=arguments.port)
        except (OSError, ValueError, RuntimeError) as error:
            return {"outcome": "failed", "run_id": arguments.run_id, "failed_step": "prepare_local",
                    "error_type": type(error).__name__, "error": str(error)}
    if arguments.operation == "build-image":
        from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import build_image

        return build_image(root, run_id=arguments.run_id)
    if arguments.operation == "verify-image":
        from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import verify_image

        return verify_image(root, run_id=arguments.run_id)
    if arguments.operation == "local":
        return _run_local(root, arguments)
    return _invoke_public(root, arguments)


def _project_root(supplied):
    root = supplied.resolve(strict=True)
    if supplied.is_symlink() or not root.is_dir() or root == Path(root.anchor):
        raise ValueError("release-project-root-invalid")
    return root


def _invalid_selection(run_id):
    return {"outcome": "failed", "run_id": run_id, "failed_step": "validate_project_selection",
            "error_type": "LocalReleaseError", "error": "local-release-project-selection-invalid",
            "effects": []}


def _run_local(root, arguments):
    from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import run_local_release, run_snapshot_release

    if arguments.status or arguments.abort:
        return run_local_release(root, run_id=arguments.run_id, mode="abort" if arguments.abort else "status")
    if arguments.continue_run:
        return _continue_local(root, arguments.run_id, run_local_release, run_snapshot_release)
    if arguments.prepare_environment:
        result = run_local_release(root, run_id=arguments.run_id, mode="prepare")
        result.update(run_id=arguments.run_id, project_root=str(root))
        return result
    options = {"resume": True} if arguments.resume else {}
    options.update({"functional_suite": arguments.suite, "started_at": time()} if arguments.suite is not None else {})
    if arguments.test_modules is not None:
        options["test_modules"] = tuple(arguments.test_modules)
    if arguments.image_mode is not None:
        options["image_mode"] = arguments.image_mode
    if arguments.target_project_root is None:
        if not arguments.resume:
            options.setdefault("image_mode", "refresh")
            print(f"Local Release run ID: {arguments.run_id}", file=sys.stderr, flush=True)
        if arguments.changed_paths:
            return _start_scoped_local(root, arguments, options, run_snapshot_release)
        result = run_local_release(root, run_id=arguments.run_id, **options)
        result.update(run_id=arguments.run_id, project_root=str(root))
        return result
    try:
        target = _project_root(arguments.target_project_root)
    except (OSError, ValueError):
        return _invalid_selection(arguments.run_id)
    result = run_snapshot_release(
        root, target_root=target, source_revision=arguments.source_revision, run_id=arguments.run_id, **options,
    )
    result.update(run_id=arguments.run_id, source_root=str(root), target_root=str(target),
                  source_revision=arguments.source_revision)
    return result


def _start_scoped_local(target, arguments, options, run_snapshot_release):
    from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import prepare_local

    try:
        prepared = prepare_local(target, run_id=arguments.run_id, base=arguments.base,
                                 changed_paths=arguments.changed_paths)
    except (OSError, ValueError, RuntimeError) as error:
        return {"outcome": "failed", "run_id": arguments.run_id, "failed_step": "prepare_local",
                "error_type": type(error).__name__, "error": str(error)}
    source = Path(prepared["project_root"])
    revision = prepared["revision"]
    print(f"Local Release source: {source} at {revision}", file=sys.stderr, flush=True)
    result = run_snapshot_release(
        source, target_root=target, source_revision=revision, run_id=arguments.run_id, **options,
    )
    return result | {"run_id": arguments.run_id, "project_root": str(target), "source_root": str(source),
                     "source_revision": revision}


def _continue_local(target, run_id, run_local_release, run_snapshot_release):
    state = run_local_release(target, run_id=run_id, mode="status")
    if state["outcome"] != "completed":
        return state
    run_id = state["run_id"]
    context = state["docker_context"]
    engine = None if context is None else ("orbstack" if context == "orbstack" else "docker")
    with _engine_environment(engine):
        if state["source_root"] is None:
            result = run_local_release(target, run_id=run_id, resume=True)
        else:
            source = _project_root(Path(state["source_root"]))
            revision = state["source_revision"]
            if not state["delivery_started"]:
                env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
                revision = subprocess.check_output(
                    ("git", "rev-parse", "--verify", "HEAD"), cwd=source, env=env, text=True, timeout=30,
                ).strip()
            result = run_snapshot_release(
                source, target_root=target, source_revision=revision, run_id=run_id, resume=True,
            )
    return result | {"run_id": run_id, "project_root": str(target)}


def _run_image(arguments: argparse.Namespace) -> dict[str, object]:
    from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import (
        launch_shared_image,
    )

    result = launch_shared_image(
        host_settings=arguments.host_settings,
        image=arguments.image,
        apply=arguments.apply,
        verify_mcp=arguments.verify_mcp,
        startup_timeout=arguments.startup_timeout,
        readiness_timeout=arguments.readiness_timeout,
        **(
            {"mounted_folder": arguments.mounted_folder}
            if arguments.mounted_folder is not None else {}
        ),
    )
    if result.get("mode") == "dry-run" or result.get("ready") is True:
        result["outcome"] = "completed"
    return result


def _invoke_public(root: Path, arguments: argparse.Namespace) -> dict[str, object]:
    from LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__shared import run_public_release

    draft = _read_draft(arguments.content_draft)
    try:
        return run_public_release(
            root, run_id=arguments.run_id, base_ref=arguments.base, head_ref=arguments.head, content_draft=draft,
        )
    except ValueError as error:
        return {
            "outcome": "failed", "run_id": arguments.run_id,
            "failed_step": "changelog", "error_type": type(error).__name__, "error": str(error),
        }


def main(argv: list[str] | None = None) -> int:
    arguments = _arguments(argv)
    maintenance = any(getattr(arguments, key, False) for key in ("status", "prepare_environment", "continue_run", "abort"))
    engine = None if maintenance else getattr(arguments, "engine", None)
    try:
        with _engine_environment(engine), redirect_stdout(sys.stderr):
            result = _invoke(arguments)
    except KeyboardInterrupt:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": "KeyboardInterrupt",
        }
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": type(error).__name__,
        }
    print(json.dumps(result, ensure_ascii=False))
    if result.get("error_type") == "KeyboardInterrupt":
        return 130
    return 0 if result.get("outcome") == "completed" else 1
