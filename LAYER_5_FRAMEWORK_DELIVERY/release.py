"""Run the Project release commands directly from the host."""


from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import json
import os
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY))


def _arguments(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation in ("local", "public"):
        command = commands.add_parser(operation)
        command.add_argument("--project-root", type=Path, default=REPOSITORY)
        command.add_argument("--run-id", required=True)
        if operation == "public":
            command.add_argument("--base", default="origin/main", help="PR base Git ref")
            command.add_argument("--head", default="amm/dev", help="PR head Git ref")
            command.add_argument(
                "--content-draft", type=Path, help="UTF-8 JSON with the reviewed change entries"
            )
        else:
            command.add_argument(
                "--image-mode",
                choices=("refresh", "existing"),
                default="refresh",
                help="candidate image mode; both use the checked-in build assets",
            )
            command.add_argument(
                "--test-module",
                action="append",
                dest="test_modules",
                metavar="PATH",
                help="repeatable relative source test module for focused validation",
            )
    return parser.parse_args(argv)


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
    root = arguments.project_root.resolve(strict=True)
    if arguments.project_root.is_symlink() or not root.is_dir() or root == Path(root.anchor):
        raise ValueError("release-project-root-invalid")
    pattern = (
        r"[A-Za-z0-9][A-Za-z0-9._:-]*"
        if arguments.operation == "public"
        else r"[A-Za-z0-9][A-Za-z0-9._-]*"
    )
    if re.fullmatch(pattern, arguments.run_id) is None:
        raise ValueError("release-run-id-invalid")
    if arguments.operation == "local":
        from LAYER_5_FRAMEWORK_DELIVERY.RELEASE_VERSION.RELEASE_VERSION__family_pub import run_local_release

        options = {}
        if arguments.test_modules is not None:
            options["test_modules"] = tuple(arguments.test_modules)
        return run_local_release(
            root, run_id=arguments.run_id, image_mode=arguments.image_mode, **options
        )
    from LAYER_5_FRAMEWORK_DELIVERY.PUBLIC_RELEASE.PUBLIC_RELEASE__family_pub import (
        PublicReleaseError,
        run_public_release,
    )

    draft = _read_draft(arguments.content_draft)
    try:
        return run_public_release(
            root, run_id=arguments.run_id, base_ref=arguments.base, head_ref=arguments.head, content_draft=draft,
        )
    except PublicReleaseError as error:
        return {
            "outcome": "failed", "run_id": arguments.run_id,
            "failed_step": "changelog", "error_type": type(error).__name__, "error": str(error),
        }


def main(argv: list[str] | None = None) -> int:
    arguments = _arguments(argv)
    try:
        with redirect_stdout(sys.stderr):
            result = _invoke(arguments)
    except KeyboardInterrupt:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": "KeyboardInterrupt",
        }
    except (OSError, ValueError, RuntimeError) as error:
        result = {
            "outcome": "failed",
            "failed_step": "invocation",
            "error_type": type(error).__name__,
        }
    print(json.dumps(result, ensure_ascii=False))
    if result.get("error_type") == "KeyboardInterrupt":
        return 130
    return 0 if result.get("outcome") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
