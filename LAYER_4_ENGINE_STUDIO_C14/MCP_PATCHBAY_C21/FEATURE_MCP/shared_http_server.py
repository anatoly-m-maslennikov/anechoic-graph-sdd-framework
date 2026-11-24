
"""Shared host Streamable HTTP transport for multiple Project gateways."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from concurrent.futures import CancelledError as FutureCancelledError
from inspect import isawaitable
from pathlib import Path
from typing import Any, Callable

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from MCP_PATCHBAY_C21.FEATURE_MCP.health_page import render_health_page
from MCP_PATCHBAY_C21.FEATURE_MCP.http_server import PORT, _accepts_html, streamable_app
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import http_log_config, run_startup, runtime_log_level, warning

from MCP_PATCHBAY_C21.FEATURE_MCP.shared_backend import SharedBackendGateway


def _snapshot_failure() -> None:
    warning("shared_health_snapshot_unavailable")

async def _snapshot(gateway: Any) -> Mapping[str, Any]:
    """Read the already-published host frontier without probing a Project."""
    reader = getattr(gateway, "status", None)
    if not callable(reader):
        _snapshot_failure()
        return {}
    try:
        value = reader()
        if isawaitable(value):
            value = await value
    except FutureCancelledError:
        raise
    except Exception:
        _snapshot_failure()
        return {}
    if not isinstance(value, Mapping):
        _snapshot_failure()
        return {}
    return value


def _ready(snapshot: Mapping[str, Any]) -> bool:
    initialized = snapshot.get("initialized")
    return type(initialized) is bool and initialized and isinstance(
        snapshot.get("advertised_tools"), list,
    )


async def health(request: Request, gateway: Any):
    """Serve one read-only host health snapshot."""
    snapshot = await _snapshot(gateway)
    ready = _ready(snapshot)
    status_code = 200 if ready else 503
    if not _accepts_html(request.headers.get("accept")):
        return JSONResponse({"ready": ready}, status_code=status_code)
    return HTMLResponse(
        render_health_page(snapshot, ready=ready, gateway=gateway),
        status_code=status_code,
        headers={"Cache-Control": "no-store"},
    )


def create_app(config: Any, *, gateway_factory: Callable[..., Any] = SharedBackendGateway):
    """Create one guarded host app; Project selection stays inside the router."""
    gateway = gateway_factory(config)

    async def health_endpoint(request: Request):
        return await health(request, gateway)

    return streamable_app(gateway, health_endpoint, shared=True)


def _serve(args: argparse.Namespace) -> Any:
    import uvicorn

    app = create_app(args.host_settings)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level=runtime_log_level().lower(), access_log=False,
                log_config=http_log_config())


def main(argv: list[str] | None = None) -> Any:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host-settings", type=Path)
    args = parser.parse_args(argv)
    return run_startup(
        lambda: _serve(args), operation="mcp_shared_http_startup",
    )


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["create_app", "health", "main"]
