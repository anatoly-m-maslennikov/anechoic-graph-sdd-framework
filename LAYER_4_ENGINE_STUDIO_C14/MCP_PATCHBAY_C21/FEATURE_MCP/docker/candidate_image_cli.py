"""Build and clean up an attributed current-source Test Suite image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from .image_docker_client import bounded_run as _bounded_run
from .docker__shared import ImageManager

ATTEMPT_LABEL = "org.anechoic.full-test-suite.attempt"


def _executor(attempt: str):
    def execute(argv, **kwargs):
        build = argv[:2] == ["docker", "build"]
        if build:
            argv = [*argv[:2], "--label", f"{ATTEMPT_LABEL}={attempt}", *argv[2:]]
        return _bounded_run(
            argv, cwd=kwargs["cwd"], timeout=kwargs["timeout"], capture_stdout=not build,
            buildx_config=kwargs.get("env", {}).get("BUILDX_CONFIG"),
        )
    return execute


def _build_image(root: Path, scratch: Path, attempt: str, *, use_packaged_assets: bool) -> str:
    manager = ImageManager(root, executor=_executor(attempt), build_temp_root=scratch, project_root=root)
    identity = manager.identity(use_packaged_assets=use_packaged_assets)
    return manager._build(identity, use_packaged_assets=use_packaged_assets)


def _remove_owned_image(root: Path, image: str, attempt: str) -> None:
    """An in-use image is retained; no container is removed by this owner."""
    try:
        observed = _bounded_run(["docker", "image", "inspect", image], cwd=root, timeout=30)
        if observed.returncode != 0:
            raise OSError("test image inspection failed")
        labels = json.loads(observed.stdout)[0]["Config"]["Labels"]
        if not isinstance(labels, dict) or labels.get(ATTEMPT_LABEL) != attempt:
            raise OSError("test image attribution differs")
        containers = _bounded_run(
            ["docker", "container", "ls", "--all", "--filter", f"ancestor={image}", "--quiet"],
            cwd=root, timeout=30,
        )
        if containers.returncode != 0 or containers.stdout.strip():
            raise OSError("test image may still be in use; retained")
        removed = _bounded_run(["docker", "image", "rm", image], cwd=root, timeout=30)
        if removed.returncode != 0:
            raise OSError("non-force test image removal failed; retained")
    except (OSError, ValueError, KeyError, IndexError, TypeError, subprocess.TimeoutExpired) as error:
        print(f"Test image cleanup: {image}: {error}", file=sys.stderr)


def _real_directory(path: Path) -> bool:
    return path.is_absolute() and path.is_dir() and path.resolve(strict=True) == path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)
    build = subcommands.add_parser("build")
    cleanup = subcommands.add_parser("cleanup")
    for command in (build, cleanup):
        command.add_argument("--project-root", type=Path, required=True)
        command.add_argument("--attempt", required=True)
    build.add_argument("--scratch", type=Path, required=True)
    build.add_argument("--packaged-assets", action="store_true")
    cleanup.add_argument("--image", required=True)
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[0-9a-f]{32}", args.attempt):
        parser.error("attempt must be 32 lowercase hexadecimal characters")
    if not _real_directory(args.project_root):
        parser.error("project root must be a resolved directory")
    if args.command == "build":
        parent = args.project_root / ".anechoic_tmp/tests/full-suite-integration"
        if not _real_directory(args.scratch) or not args.scratch.is_relative_to(parent) or args.scratch == parent:
            parser.error("scratch must be a resolved directory inside the Test Suite scratch root")
        print(_build_image(args.project_root, args.scratch, args.attempt,
                           use_packaged_assets=args.packaged_assets))
    else:
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", args.image):
            parser.error("image must be an immutable sha256 ID")
        _remove_owned_image(args.project_root, args.image, args.attempt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
