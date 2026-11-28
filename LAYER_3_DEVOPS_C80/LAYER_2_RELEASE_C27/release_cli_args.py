"""Parse and validate the release command line."""

import argparse
from pathlib import Path
import re
import sys
from uuid import uuid4


def parse_arguments(argv, repository, description):
    parser = argparse.ArgumentParser(description=description)
    commands = parser.add_subparsers(dest="operation", required=True)
    for operation in (
        "local",
        "public",
        "build-image",
        "verify-image",
        "prepare-local",
    ):
        command = commands.add_parser(operation)
        command.add_argument("--project-root", type=Path, default=repository)
        command.add_argument("--run-id", required=operation != "local")
        if operation in ("local", "build-image", "verify-image"):
            _engine_argument(command)
        _configure_command(operation, command)
    _image_arguments(commands.add_parser("run-image"))
    arguments = parser.parse_args(argv)
    if (
        arguments.operation in ("local", "verify-image")
        and arguments.run_id is not None
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", arguments.run_id)
        is None
    ):
        parser.error(
            "--run-id must contain only letters, digits, dots, "
            "underscores, or hyphens"
        )
    if arguments.operation == "local":
        _validate_local_arguments(parser, arguments)
    return arguments


def _configure_command(operation, command):
    if operation == "public":
        command.add_argument(
            "--base", default="origin/main", help="PR base Git ref"
        )
        command.add_argument(
            "--head", default="amm/dev", help="PR head Git ref"
        )
        command.add_argument(
            "--content-draft",
            type=Path,
            help="UTF-8 JSON with the reviewed change entries",
        )
    elif operation == "prepare-local":
        command.add_argument("--base", required=True, help="exact base commit")
        command.add_argument(
            "--changed-path",
            action="append",
            required=True,
            dest="changed_paths",
            metavar="PATH",
            help="literal repository-relative file addition, "
            "edit, or deletion",
        )
        command.add_argument(
            "--port",
            required=True,
            type=int,
            help="isolated loopback MCP port",
        )
    elif operation == "local":
        _local_arguments(command)


def _image_arguments(run_image):
    _engine_argument(run_image)
    location = run_image.add_mutually_exclusive_group()
    location.add_argument("--host-settings", type=Path)
    location.add_argument("--mounted-folder", type=Path)
    run_image.add_argument("--image")
    run_image.add_argument("--apply", action="store_true")
    run_image.add_argument("--verify-mcp", action="store_true")
    run_image.add_argument("--startup-timeout", type=int)
    run_image.add_argument("--readiness-timeout", type=int)


def _engine_argument(command):
    command.add_argument(
        "--engine",
        choices=("orbstack", "docker"),
        default="orbstack" if sys.platform == "darwin" else "docker",
        help="container engine (default: %(default)s)",
    )


def _local_arguments(command):
    _local_actions(command)
    command.add_argument(
        "--target-project-root",
        type=Path,
        help="Project receiving the verified release",
    )
    command.add_argument(
        "--source-revision",
        help="exact Git commit for a separate release source",
    )
    command.add_argument(
        "--suite",
        choices=("full", "fast"),
        help="Functional suite (default: full)",
    )
    command.add_argument(
        "--base", help="exact base commit for a scoped release"
    )
    command.add_argument(
        "--changed-path",
        action="append",
        dest="changed_paths",
        metavar="PATH",
        help="literal file overlay for a scoped release",
    )
    command.add_argument(
        "--image-mode",
        choices=("refresh", "existing"),
        help="candidate image mode; both use the checked-in build assets",
    )
    command.add_argument(
        "--test-module",
        action="append",
        dest="test_modules",
        metavar="PATH",
        help="repeatable relative source test module for focused validation",
    )


def _local_actions(command):
    mode = command.add_mutually_exclusive_group()
    mode.add_argument(
        "--resume",
        action="store_true",
        help="continue the recorded Local Release",
    )
    mode.add_argument(
        "--continue",
        dest="continue_run",
        action="store_true",
        help="continue from the target journal",
    )
    mode.add_argument(
        "--abort",
        action="store_true",
        help="request a stop at a safe checkpoint",
    )
    mode.add_argument(
        "--status",
        action="store_true",
        help="read the recorded Local Release progress",
    )
    mode.add_argument(
        "--prepare-environment",
        action="store_true",
        help="provision and verify the checkout's test dependencies",
    )


def _validate_scoped_release(parser, arguments, target, revision):
    if arguments.base is not None or arguments.changed_paths:
        if (
            not arguments.base
            or not arguments.changed_paths
            or target is not None
            or revision is not None
            or any(
                (
                    arguments.resume,
                    arguments.status,
                    arguments.abort,
                    arguments.continue_run,
                    arguments.prepare_environment,
                )
            )
        ):
            parser.error(
                "--base and --changed-path must be used together "
                "to start a scoped Local Release"
            )


def _validate_local_arguments(parser, arguments):
    target, revision = arguments.target_project_root, arguments.source_revision
    if arguments.resume and arguments.run_id is None:
        parser.error("--resume requires --run-id")
    _validate_scoped_release(parser, arguments, target, revision)
    requested = (
        target,
        revision,
        arguments.image_mode,
        arguments.test_modules,
        arguments.suite,
    )
    if arguments.continue_run or arguments.abort:
        if any(value is not None for value in requested):
            parser.error(
                "--continue and --abort use the recorded release inputs"
            )
        return
    if arguments.run_id is None and not arguments.status:
        arguments.run_id = uuid4().hex[:12]
    if (arguments.status or arguments.prepare_environment) and any(
        value is not None for value in requested
    ):
        parser.error(
            "--status and --prepare-environment each take "
            "a single --project-root"
        )
    if (target is None) != (revision is None):
        parser.error(
            "--target-project-root and --source-revision "
            "must be supplied together"
        )
    if (
        revision is not None
        and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision) is None
    ):
        parser.error(
            "--source-revision must be an exact lowercase Git commit SHA"
        )
