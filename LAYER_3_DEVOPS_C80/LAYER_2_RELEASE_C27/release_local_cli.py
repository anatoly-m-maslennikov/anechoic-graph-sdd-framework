"""Dispatch local release actions with their recorded host inputs."""

from contextlib import contextmanager
import os
from pathlib import Path
import subprocess
import sys
from time import time


@contextmanager
def _engine_environment(engine):
    if engine is None:
        yield
        return
    saved = {
        key: os.environ.get(key) for key in ("DOCKER_CONTEXT", "DOCKER_HOST")
    }
    docker_context = "desktop-linux" if sys.platform == "darwin" else "default"
    os.environ["DOCKER_CONTEXT"] = (
        "orbstack" if engine == "orbstack" else docker_context
    )
    os.environ.pop("DOCKER_HOST", None)
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _project_root(supplied):
    root = supplied.resolve(strict=True)
    if supplied.is_symlink() or not root.is_dir() or root == Path(root.anchor):
        raise ValueError("release-project-root-invalid")
    return root


def _invalid_selection(run_id):
    return {
        "outcome": "failed",
        "run_id": run_id,
        "failed_step": "validate_project_selection",
        "error_type": "LocalReleaseError",
        "error": "local-release-project-selection-invalid",
        "effects": [],
    }


def _run_local(root, arguments):
    from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
        run_local_release,
        run_snapshot_release,
    )

    if arguments.status or arguments.abort:
        return run_local_release(
            root,
            run_id=arguments.run_id,
            mode="abort" if arguments.abort else "status",
        )
    if arguments.continue_run:
        return _continue_local(
            root, arguments.run_id, run_local_release, run_snapshot_release
        )
    if arguments.prepare_environment:
        result = run_local_release(
            root, run_id=arguments.run_id, mode="prepare"
        )
        result.update(run_id=arguments.run_id, project_root=str(root))
        return result
    options = {"resume": True} if arguments.resume else {}
    options.update(
        {"functional_suite": arguments.suite, "started_at": time()}
        if arguments.suite is not None
        else {}
    )
    if arguments.test_modules is not None:
        options["test_modules"] = tuple(arguments.test_modules)
    if arguments.image_mode is not None:
        options["image_mode"] = arguments.image_mode
    return _start_selected_local(
        root, arguments, options, run_local_release, run_snapshot_release
    )


def _start_selected_local(
    root, arguments, options, run_local_release, run_snapshot_release
):
    if arguments.target_project_root is None:
        if not arguments.resume:
            options.setdefault("image_mode", "refresh")
            print(
                f"Local Release run ID: {arguments.run_id}",
                file=sys.stderr,
                flush=True,
            )
        if arguments.changed_paths:
            return _start_scoped_local(
                root, arguments, options, run_snapshot_release
            )
        result = run_local_release(root, run_id=arguments.run_id, **options)
        result.update(run_id=arguments.run_id, project_root=str(root))
        return result
    try:
        target = _project_root(arguments.target_project_root)
    except OSError, ValueError:
        return _invalid_selection(arguments.run_id)
    result = run_snapshot_release(
        root,
        target_root=target,
        source_revision=arguments.source_revision,
        run_id=arguments.run_id,
        **options,
    )
    result.update(
        run_id=arguments.run_id,
        source_root=str(root),
        target_root=str(target),
        source_revision=arguments.source_revision,
    )
    return result


def _start_scoped_local(target, arguments, options, run_snapshot_release):
    from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
        prepare_local,
    )

    try:
        prepared = prepare_local(
            target,
            run_id=arguments.run_id,
            base=arguments.base,
            changed_paths=arguments.changed_paths,
        )
    except (OSError, ValueError, RuntimeError) as error:
        return {
            "outcome": "failed",
            "run_id": arguments.run_id,
            "failed_step": "prepare_local",
            "error_type": type(error).__name__,
            "error": str(error),
        }
    source = Path(prepared["project_root"])
    revision = prepared["revision"]
    print(
        f"Local Release source: {source} at {revision}",
        file=sys.stderr,
        flush=True,
    )
    result = run_snapshot_release(
        source,
        target_root=target,
        source_revision=revision,
        run_id=arguments.run_id,
        **options,
    )
    return result | {
        "run_id": arguments.run_id,
        "project_root": str(target),
        "source_root": str(source),
        "source_revision": revision,
    }


def _continue_local(target, run_id, run_local_release, run_snapshot_release):
    state = run_local_release(target, run_id=run_id, mode="status")
    if state["outcome"] != "completed":
        return state
    run_id = state["run_id"]
    context = state["docker_context"]
    engine = (
        None
        if context is None
        else ("orbstack" if context == "orbstack" else "docker")
    )
    with _engine_environment(engine):
        if state["source_root"] is None:
            result = run_local_release(target, run_id=run_id, resume=True)
        else:
            source = _project_root(Path(state["source_root"]))
            revision = state["source_revision"]
            if not state["delivery_started"]:
                env = {
                    key: value
                    for key, value in os.environ.items()
                    if not key.startswith("GIT_")
                }
                revision = subprocess.check_output(
                    ("git", "rev-parse", "--verify", "HEAD"),
                    cwd=source,
                    env=env,
                    text=True,
                    timeout=30,
                ).strip()
            result = run_snapshot_release(
                source,
                target_root=target,
                source_revision=revision,
                run_id=run_id,
                resume=True,
            )
    return result | {"run_id": run_id, "project_root": str(target)}
