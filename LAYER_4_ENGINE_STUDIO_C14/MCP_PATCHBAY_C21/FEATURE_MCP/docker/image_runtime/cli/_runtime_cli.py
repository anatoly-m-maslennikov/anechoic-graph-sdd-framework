"""Command line for explicit Project Docker operations."""

import argparse
import json
import os
from pathlib import Path


def _project_mcp_port(value):
    try:
        port = int(value)
    except (TypeError, ValueError) as error:
        raise argparse.ArgumentTypeError(
            "--port must be an integer in 1..65535"
        ) from error
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(
            "--port must be an integer in 1..65535"
        )
    return port


def _parser(source_root, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--project-root", type=Path, default=source_root)
    parser.add_argument("--image", help=argparse.SUPPRESS)
    _add_launch_options(parser)
    parser.add_argument(
        "--image-mode",
        choices=("refresh", "existing"),
        help="Asset selection for build (default: refresh)",
    )
    parser.add_argument(
        "--port",
        type=_project_mcp_port,
        help=(
            "Assert the Project Settings HTTP port for project-mcp "
            "(1..65535)"
        ),
    )
    parser.add_argument(
        "--output",
        choices=["json", "url"],
        default="json",
        help="Project MCP result format",
    )
    parser.add_argument(
        "operation",
        choices=[
            "build",
            "status",
            "logs",
            "mcp",
            "mcp-http-start",
            "mcp-http-stop",
            "mcp-http-status",
            "project-mcp",
        ],
    )
    return parser


def run_cli(runtime_type, source_root, description):
    parser = _parser(source_root, description)
    args = parser.parse_args()
    if args.image_mode is not None and args.operation != "build":
        parser.error("--image-mode applies to build only")
    if args.operation == "project-mcp":
        return _launch_project_mcp(args)
    runtime = runtime_type(args.project_root, image=args.image)
    if args.operation == "build":
        if not 0 < args.build_timeout <= 600:
            parser.error("--build-timeout must be within (0, 600]")
        print(
            runtime.build(
                use_packaged_assets=args.image_mode == "existing",
                timeout=args.build_timeout,
            )
        )
    elif args.operation == "status":
        print(json.dumps(runtime.status()))
    elif args.operation == "logs":
        runtime.call("logs", "--tail", "100", capture=False)
    elif args.operation == "mcp-http-start":
        print(json.dumps(runtime.mcp_http_start()))
    elif args.operation == "mcp-http-stop":
        print(json.dumps(runtime.mcp_http_stop()))
    elif args.operation == "mcp-http-status":
        print(json.dumps(runtime.mcp_http_status()))
    else:
        runtime.prepare()
        runtime._ensure_launch_image()
        os.execvpe(
            "docker",
            runtime.command("run", "--rm", "--no-deps", "-T", "mcp"),
            runtime.environment(),
        )


def _launch_project_mcp(args):
    from MCP_PATCHBAY_C21.FEATURE_MCP.docker.project.project__shared import (
        Launcher,
    )

    result = Launcher().launch(
        args.project_root,
        None,
        control_root=args.control_root,
        image=args.image,
        source_root=args.source_root,
        timeout=args.startup_timeout,
        port=args.port,
        build_if_missing=not args.no_build,
        build_timeout=args.build_timeout,
    )
    ready = (
        result.get("disposition") in ("started", "reused")
        and result.get("readiness") is True
    )
    print(
        result["url"]
        if args.output == "url" and ready
        else json.dumps(result, sort_keys=True)
    )
    return 0 if ready else 1


def _add_launch_options(parser):
    parser.add_argument(
        "--control-root",
        help=(
            "Direct _anechoic_<project> or legacy .anechoic_<project> "
            "folder, when explicit selection is needed"
        ),
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        help=(
            "Explicit Framework checkout with image build inputs; required "
            "for project-mcp"
        ),
    )
    parser.add_argument(
        "--startup-timeout",
        type=float,
        default=420,
        help="Bound startup/readiness seconds (maximum 420)",
    )
    parser.add_argument(
        "--build-timeout",
        type=float,
        default=600,
        help="Bound image build seconds (maximum 600)",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="Refuse a missing compatible image instead of building",
    )
