"""Run local HTTP MCP with the Current runtime."""

import argparse
import os
from pathlib import Path

import uvicorn
from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import (
    native_runtime_gateway,
    startup_selection,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import create_app
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import (
    http_log_config,
    run_startup,
    runtime_log_level,
)
from MCP_PATCHBAY_C21.FEATURE_MCP.runtime_stack import runtime_stack


def _serve(args):
    runtime_stack()
    os.environ.setdefault("ANECHOIC_RUNTIME_PROFILE", "dev-local")
    selection = startup_selection(args.project_root)
    with native_runtime_gateway(selection) as gateway:
        app = create_app(
            args.project_root, selection=selection, runtime_gateway=gateway
        )
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=args.port,
            log_level=runtime_log_level().lower(),
            access_log=False,
            log_config=http_log_config(),
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    return run_startup(lambda: _serve(args), operation="mcp_http_startup")


if __name__ == "__main__":
    raise SystemExit(main())
