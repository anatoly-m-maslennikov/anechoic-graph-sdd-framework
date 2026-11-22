
"""Loopback-only Streamable HTTP transport for the MCP gateway."""
import argparse
from concurrent.futures import CancelledError as FutureCancelledError
from contextlib import ExitStack, asynccontextmanager
from pathlib import Path
import re

from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import native_project_gateway, native_runtime_gateway, startup_selection
from MCP_PATCHBAY_C21.FEATURE_MCP.http_paths import HEALTH_PATH, MCP_PATH
from mcp.server.transport_security import TransportSecuritySettings
from MCP_PATCHBAY_C21.FEATURE_MCP.mcp_startup_boundary import run_startup, warning
from MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web import routes as workbench_routes

PATH = MCP_PATH
PORT = 8092
MAX_REQUEST_BODY_SIZE = 16 * 1024 * 1024
SECURITY = TransportSecuritySettings(
    enable_dns_rebinding_protection=True,
    allowed_hosts=["127.0.0.1:*", "localhost:*", "[::1]:*"],
    allowed_origins=["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"],
)


class LoopbackGuard:
    """Apply loopback Host and Origin admission before the MCP ASGI application."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive)
        host = request.headers.get("host", "")
        origin = request.headers.get("origin")
        valid_host = re.fullmatch(r"(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?", host)
        valid_origin = origin is None or re.fullmatch(
            r"http://(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?", origin)
        if not valid_host:
            self._warning('http_host_rejected', 'host_admission')
            await Response(status_code=421)(scope, receive, send)
            return
        if not valid_origin:
            self._warning('http_origin_rejected', 'origin_admission')
            await Response(status_code=403)(scope, receive, send)
            return
        await self.app(scope, receive, send)

    def _warning(self, code, operation):
        warning(code)


def _accepts_html(value):
    """Honor explicit text/html only when its quality is not lower than JSON."""
    if not isinstance(value, str):
        return False
    html_quality = None
    explicit_json_quality = None
    wildcard_quality = 0.0
    for item in value.split(","):
        parts = [part.strip() for part in item.split(";")]
        if not parts:
            continue
        quality = 1.0
        for parameter in parts[1:]:
            key, separator, raw = parameter.partition("=")
            if key.strip().lower() != "q" or not separator:
                continue
            try:
                quality = float(raw.strip())
            except ValueError:
                quality = 0.0
        media_type = parts[0].lower()
        if media_type == "text/html":
            html_quality = max(html_quality or 0.0, quality)
        elif media_type == "application/json":
            explicit_json_quality = max(explicit_json_quality or 0.0, quality)
        elif media_type == "*/*":
            wildcard_quality = max(wildcard_quality, quality)
    json_quality = (
        explicit_json_quality if explicit_json_quality is not None else wildcard_quality
    )
    return (
        html_quality is not None
        and 0.0 < html_quality <= 1.0
        and html_quality >= json_quality
    )


async def health(gateway):
    ready = gateway.ready
    payload = {"ready": ready}
    observer = getattr(gateway, "health_observations", None)
    if observer is not None:
        try:
            observer.snapshot()
        except FutureCancelledError:
            raise
        except Exception:
            warning("health_observations_unavailable")
            payload["health_warning"] = "health observations unavailable"
    return JSONResponse(payload, status_code=200 if ready else 503)


def create_app(root, *, selection=None, gateway_factory=None, control_root=None, runtime_gateway=None):
    if runtime_gateway is not None:
        gateway = runtime_gateway
    elif gateway_factory is not None:
        if selection is not None or not control_root:
            raise ValueError("Injected gateway requires an explicit control root")
        gateway = gateway_factory(root, control_root)
    else:
        selected = selection if selection is not None else startup_selection(root, control_root)
        gateway = native_project_gateway(root, selection=selected)
    server = gateway.build_server()

    async def readiness(_request):
        return await health(gateway)

    routes = [Route(HEALTH_PATH, readiness), *workbench_routes(gateway)]
    app = server.streamable_http_app(
        streamable_http_path=PATH,
        transport_security=SECURITY,
        max_request_body_size=MAX_REQUEST_BODY_SIZE,
        host="127.0.0.1",
        custom_starlette_routes=routes,
    )
    inner_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        async with inner_lifespan(application):
            await gateway.initialize()
            try:
                yield
            finally:
                await gateway.close()

    app.router.lifespan_context = lifespan
    guarded = LoopbackGuard(app)
    guarded.gateway = gateway
    guarded.starlette_app = app
    return guarded


def _serve(args, *, gateway_factory=None):
    if args.host != "0.0.0.0" or args.port != PORT:
        raise ValueError("HTTP MCP requires the container bind 0.0.0.0:8092")
    import uvicorn

    with ExitStack() as stack:
        if gateway_factory is not None:
            app = create_app(args.project_root, gateway_factory=gateway_factory, control_root=args.control_root)
        else:
            selection = startup_selection(args.project_root, args.control_root, args.instance_id, args.host_project_root)
            gateway = stack.enter_context(native_runtime_gateway(selection))
            app = create_app(args.project_root, selection=selection, runtime_gateway=gateway)
        uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


def main(argv=None, *, gateway_factory=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--control-root")
    parser.add_argument("--instance-id")
    parser.add_argument("--host-project-root")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=PORT, type=int)
    args = parser.parse_args(argv)
    if gateway_factory is not None and (
        not args.control_root or args.instance_id is not None or args.host_project_root is not None
    ):
        parser.error("Native selection requires --control-root and derives its own instance identity")
    return run_startup(
        lambda: _serve(args, gateway_factory=gateway_factory), operation='mcp_http_startup',
    )


if __name__ == "__main__":
    raise SystemExit(main())
