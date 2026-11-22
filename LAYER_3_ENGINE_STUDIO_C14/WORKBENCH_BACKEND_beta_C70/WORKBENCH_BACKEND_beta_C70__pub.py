"""Serve the stateless Beta Workbench API on a private Unix socket."""
import argparse
import json
import os
from pathlib import Path
import re
import socket
import stat
import threading
import sys

import httpx2
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

_FIELDS = {"name", "arguments", "instance_id", "session_id", "public_base_url", "asserted_project_root"}
_TOOL = json.loads(Path(__file__).with_name("query_run.json").read_text(encoding="utf-8"))


def failure(code, message):
    rejected = code in {"tool_input_invalid", "tool_unavailable"}
    diagnostic = "Unknown Tool" if code == "tool_unavailable" else code if rejected else f"{code}: {message}"
    return JSONResponse({"error": {"code": code, "message": message, "tool_result": {
        "outcome": "rejected" if rejected else "failed", "diagnostics": [diagnostic]}}})


def _tool_route(upstream, database_socket, instance_id, project_root, host_root, blacklist):
    async def invoke(request):
        try:
            raw = await request.body()
            if len(raw) > 65536:
                raise ValueError("Request is too large")
            data = json.loads(raw)
            if (not isinstance(data, dict) or set(data) != _FIELDS or data["instance_id"] != instance_id
                    or not isinstance(data["name"], str) or not isinstance(data["arguments"], dict)
                    or any(data[k] is not None and (not isinstance(data[k], str) or not data[k].strip())
                           for k in ("session_id", "public_base_url", "asserted_project_root"))):
                raise ValueError("Invalid Tool request envelope")
            if data["asserted_project_root"] not in (None, project_root, host_root):
                raise ValueError("project_root does not match the bound Project")
            if data["name"] != "query_run" or "query_run" in blacklist:
                return failure("tool_unavailable", "Unknown Tool")
            args = data["arguments"]
            if (set(args) - {"sql", "result_delivery", "result_format"} or not isinstance(args.get("sql"), str)
                    or args.get("result_delivery", "auto") not in ("auto", "inline")
                    or args.get("result_format", "json_matrix") != "json_matrix"):
                return failure("tool_input_invalid", "Only SQL and inline JSON matrix delivery are supported")
            result = await upstream(database_socket, "POST", "/database", json={"instance_id": instance_id, "sql": args["sql"]})
            if "error" in result:
                error = result["error"]
                return failure("query_error", str(error.get("message", "Query failed")) if isinstance(error, dict) else "Query failed")
            value = result["result"]
            if not isinstance(value, dict) or set(value) != {"columns", "rows"}:
                raise ValueError("Invalid Kernel response")
            return JSONResponse({"result": {"value": value, "text": None}})
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError) as error:
            return failure("value_error", str(error))
        except httpx2.HTTPError:
            return failure("workbench_unavailable", "Kernel unavailable")

    return invoke


def create_app(instance_id, manifest_sha256, project_root, database_socket, orchestrator_socket,
               *, host_root=None, blacklist=()):
    async def upstream(socket_path, method, path, **kwargs):
        async with httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=socket_path),
                                      base_url="http://private", timeout=10, trust_env=False) as client:
            response = await client.request(method, path, **kwargs)
            data = response.json()
            if not isinstance(data, dict) or set(data) not in ({"result"}, {"error"}):
                raise ValueError("Invalid upstream response")
            return data

    async def health(_request):
        try:
            data = await upstream(database_socket, "GET", "/health")
            result = data.get("result", {})
            if (result.get("instance_id") != instance_id or result.get("manifest_sha256") != manifest_sha256
                    or type(result.get("pid")) is not int):
                raise ValueError("Invalid Kernel binding")
            return JSONResponse({"ready": True, "instance_id": instance_id, "manifest_sha256": manifest_sha256,
                                 "pid": os.getpid(), "kernel_pid": result["pid"]})
        except (httpx2.HTTPError, ValueError, TypeError, AttributeError):
            return JSONResponse({"ready": False, "instance_id": instance_id, "manifest_sha256": manifest_sha256,
                                 "pid": os.getpid(), "kernel_pid": None}, status_code=503)

    def bound(request):
        return list(request.query_params.multi_items()) == [("instance_id", instance_id)]

    async def catalog(request):
        if not bound(request):
            return failure("value_error", "Invalid Tool request binding")
        tools = [] if "query_run" in blacklist else [_TOOL]
        return JSONResponse({"result": {"tools": tools, "blacklist": list(blacklist)}})

    async def worker_runs(request):
        if not bound(request):
            return failure("value_error", "Invalid Worker Run request binding")
        try:
            result = await upstream(orchestrator_socket, "GET", "/jobs/worker-runs", params={"instance_id": instance_id})
            return JSONResponse(result)
        except (httpx2.HTTPError, ValueError, TypeError):
            return failure("workbench_unavailable", "Orchestrator unavailable")

    invoke = _tool_route(upstream, database_socket, instance_id, project_root, host_root, blacklist)
    return Starlette(routes=[Route("/health", health), Route("/tools", catalog),
                             Route("/tools", invoke, methods=["POST"]), Route("/jobs/worker-runs", worker_runs)])


def socket_path(value):
    path = Path(value)
    parent = path.parent
    info = parent.stat()
    if (not path.is_absolute() or str(path) != value or path.exists() or path.is_symlink()
            or parent.resolve(strict=True) != parent or parent.is_symlink()
            or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) & 0o077):
        raise ValueError("Socket directory is unavailable or unsafe")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("socket", "database-socket", "orchestrator-socket", "instance-id", "manifest-sha256", "project-root"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    if not args.instance_id or re.fullmatch(r"[0-9a-f]{64}", args.manifest_sha256) is None:
        parser.error("Invalid Project binding")
    if not Path(args.project_root).is_absolute():
        parser.error("Project root must be absolute")
    path = socket_path(args.socket)
    app = create_app(args.instance_id, args.manifest_sha256, args.project_root, args.database_socket, args.orchestrator_socket)
    serve(path, app)


def serve(path, app):
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning"))
    def watch_parent():
        while os.read(sys.stdin.fileno(), 4096):
            pass
        server.should_exit = True
    threading.Thread(target=watch_parent, daemon=True).start()
    os.umask(0o077)
    bound = False
    try:
        with socket.socket(socket.AF_UNIX) as listener:
            listener.bind(str(path))
            bound = True
            listener.listen(128)
            server.run(sockets=[listener])
    finally:
        if bound:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
