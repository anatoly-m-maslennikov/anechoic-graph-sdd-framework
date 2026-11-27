"""MCP entry point for the native Workbench gateway."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import (
    native_runtime_gateway,
    startup_selection,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import run_startup


def _serve_stdio(args, *, gateway_factory=None):
    if gateway_factory is not None:
        asyncio.run(
            gateway_factory(args.project_root, args.control_root).serve()
        )
        return
    os.environ.setdefault("ANECHOIC_RUNTIME_STACK", "beta_next")
    os.environ.setdefault("ANECHOIC_RUNTIME_PROFILE", "dev-local")
    selection = startup_selection(
        args.project_root,
        args.control_root,
        args.instance_id,
        args.host_project_root,
    )
    with native_runtime_gateway(selection) as gateway:
        asyncio.run(gateway.serve())


def main(argv=None, *, gateway_factory=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--control-root")
    parser.add_argument("--instance-id")
    parser.add_argument("--host-project-root")
    parser.add_argument(
        "--transport", choices=("stdio", "streamable-http"), default="stdio"
    )
    args = parser.parse_args(argv)
    if gateway_factory is not None and (
        not args.control_root
        or args.instance_id is not None
        or args.host_project_root is not None
    ):
        parser.error(
            (
                "Native selection requires --control-root and derives its own "
                "instance identity"
            )
        )
    if args.transport == "stdio":
        return run_startup(
            lambda: _serve_stdio(args, gateway_factory=gateway_factory),
            operation="mcp_stdio_startup",
        )
    else:
        from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import main as serve_http

        http_argv = ["--project-root", str(args.project_root)]
        for flag, value in (
            ("--control-root", args.control_root),
            ("--instance-id", args.instance_id),
            ("--host-project-root", args.host_project_root),
        ):
            if value is not None:
                http_argv += [flag, value]
        if gateway_factory is not None:
            return serve_http(http_argv, gateway_factory=gateway_factory)
        return serve_http(http_argv)


if __name__ == "__main__":
    raise SystemExit(main())
