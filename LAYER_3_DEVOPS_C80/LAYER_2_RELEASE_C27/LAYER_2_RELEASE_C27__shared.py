"""Run the Project release commands directly from the host."""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
REPOSITORY = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from release_cli_args import parse_arguments  # noqa: E402
from release_local_cli import (  # noqa: E402
    _engine_environment,
    _invalid_selection,
    _project_root,
    _run_local,
)


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    return parse_arguments(argv, REPOSITORY, __doc__)


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
    except OSError, ValueError:
        if arguments.operation in ("local", "verify-image"):
            return _invalid_selection(arguments.run_id)
        raise
    pattern = (
        r"[A-Za-z0-9][A-Za-z0-9._:-]*"
        if arguments.operation == "public"
        else r"[A-Za-z0-9][A-Za-z0-9._-]*"
    )
    if (
        arguments.run_id is not None
        and re.fullmatch(pattern, arguments.run_id) is None
    ):
        raise ValueError("release-run-id-invalid")
    if arguments.operation == "prepare-local":
        return _prepare_local(root, arguments)
    if arguments.operation == "build-image":
        from LAYER_1_RUNTIME_IMAGES_C81.\
            LAYER_1_RUNTIME_IMAGES_C81__shared import (
            build_image,
        )  # fmt: skip

        return build_image(root, run_id=arguments.run_id)
    if arguments.operation == "verify-image":
        from LAYER_2_LOCAL_RELEASE_C63.\
            LAYER_2_LOCAL_RELEASE_C63__shared import (
            verify_image,
        )  # fmt: skip

        return verify_image(root, run_id=arguments.run_id)
    if arguments.operation == "local":
        return _run_local(root, arguments)
    return _invoke_public(root, arguments)


def _prepare_local(root, arguments):
    from LAYER_2_LOCAL_RELEASE_C63.\
        LAYER_2_LOCAL_RELEASE_C63__shared import (
        prepare_local,
    )  # fmt: skip

    try:
        return prepare_local(
            root,
            run_id=arguments.run_id,
            base=arguments.base,
            changed_paths=arguments.changed_paths,
            port=arguments.port,
        )
    except (OSError, ValueError, RuntimeError) as error:
        return {
            "outcome": "failed",
            "run_id": arguments.run_id,
            "failed_step": "prepare_local",
            "error_type": type(error).__name__,
            "error": str(error),
        }


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
            if arguments.mounted_folder is not None
            else {}
        ),
    )
    if result.get("mode") == "dry-run" or result.get("ready") is True:
        result["outcome"] = "completed"
    return result


def _invoke_public(
    root: Path, arguments: argparse.Namespace
) -> dict[str, object]:
    from LAYER_3_PUBLIC_RELEASE_C64.LAYER_3_PUBLIC_RELEASE_C64__shared import (
        run_public_release,
    )

    draft = _read_draft(arguments.content_draft)
    try:
        return run_public_release(
            root,
            run_id=arguments.run_id,
            base_ref=arguments.base,
            head_ref=arguments.head,
            content_draft=draft,
        )
    except ValueError as error:
        return {
            "outcome": "failed",
            "run_id": arguments.run_id,
            "failed_step": "changelog",
            "error_type": type(error).__name__,
            "error": str(error),
        }


def main(argv: list[str] | None = None) -> int:
    arguments = _arguments(argv)
    maintenance = any(
        getattr(arguments, key, False)
        for key in ("status", "prepare_environment", "continue_run", "abort")
    )
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
    except (
        OSError,
        ValueError,
        RuntimeError,
        subprocess.SubprocessError,
    ) as error:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": type(error).__name__,
        }
    print(json.dumps(result, ensure_ascii=False))
    if result.get("error_type") == "KeyboardInterrupt":
        return 130
    return 0 if result.get("outcome") == "completed" else 1
