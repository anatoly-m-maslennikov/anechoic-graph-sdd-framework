"""Own one pinned Project's private Backend and raw Tool protocol."""

import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import monotonic

import httpx2

_MODULE = (
    'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.backend_proce'
    'ss'
)


class ToolProtocolError(RuntimeError):
    def __init__(self, code, message, tool_result=None):
        self.code = code
        self.tool_result = tool_result
        super().__init__(message)


class ProjectToolSession:
    def __init__(
        self, root, *, selection, workbench_storage=None, journal_storage=None
    ):
        self.root = Path(root)
        self.selection = selection
        self._workbench_storage = workbench_storage
        self._journal_storage = journal_storage
        self._directory = None
        self._process = None
        self._http = None
        self._closed = False
        self.tools = ()
        self.tool_blacklist = frozenset()
        self._catalog_digest = None

    @property
    def ready(self):
        return (not self._closed and self._catalog_digest is not None
                and self._process is not None and self._process.poll() is None)

    @property
    def pid(self):
        return self._process.pid if self.ready else None

    def _start(self, socket):
        engine = Path(__file__).resolve().parents[3]
        root = engine.parent
        paths = (engine,)
        environment = {
            **os.environ,
            "PYTHONPATH": os.pathsep.join(map(str, paths)),
        }
        selection = self.selection
        command = [
            sys.executable,
            "-B",
            "-P",
            "-m",
            _MODULE,
            "--socket",
            str(socket),
            "--project-root",
            str(selection.root),
            "--control-root",
            selection.control_relative.as_posix(),
            "--instance-id",
            selection.instance_id,
            "--manifest-sha256",
            selection.manifest_sha256,
        ]
        if selection.host_root is not None:
            command += ["--host-project-root", str(selection.host_root)]
        if self._workbench_storage is not None:
            command += ["--default-workbench-storage", self._workbench_storage]
        if self._journal_storage is not None:
            command += ["--default-journal-storage", self._journal_storage]
        return subprocess.Popen(
            command, cwd=root, env=environment, stdin=subprocess.PIPE, stdout=2
        )

    async def initialize(self):
        if self._closed or self._process is not None:
            raise RuntimeError(
                "Project Tool session already started or closed"
            )
        try:
            self._directory = TemporaryDirectory(prefix="anechoic-api-", dir="/tmp")
            socket = Path(self._directory.name).resolve() / "api.sock"
            self._http = httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=str(socket)),
                                            base_url="http://anechoic-backend", trust_env=False, timeout=None)
            self._process = self._start(socket)
            expected = {"ready": True, "instance_id": self.selection.instance_id,
                        "manifest_sha256": self.selection.manifest_sha256, "pid": self._process.pid}
            bounded = os.getenv("ANECHOIC_TEST_IMAGE_DEADLINES") != "0"
            deadline = monotonic() + 90
            while (self._process.poll() is None
                   and (not bounded or monotonic() < deadline)):
                try:
                    response = await self._http.get("/health", timeout=0.5)
                except httpx2.TransportError:
                    await asyncio.sleep(0.05)
                    continue
                try:
                    observed = response.json()
                except ValueError as error:
                    raise RuntimeError("Invalid Backend health response") from error
                if (response.status_code != 200 or not isinstance(observed, dict)
                        or any(observed.get(key) != value for key, value in expected.items())
                        or not isinstance(observed.get("kernel_pid"), int)):
                    raise RuntimeError((
                        'Workbench Backend reported a different Project '
                        'binding'
                    ))
                timeout = max(0, deadline - monotonic()) if bounded else None
                async with asyncio.timeout(timeout):
                    catalog, digest = await self._catalog()
                self.tools = tuple(catalog["tools"])
                self.tool_blacklist = frozenset(catalog["blacklist"])
                self._catalog_digest = digest
                return
            raise RuntimeError("Workbench Backend did not start")
        except BaseException:
            await self.close()
            raise

    @staticmethod
    def _response(response):
        try:
            envelope = response.json()
        except ValueError as error:
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend response"
            ) from error
        if (
            response.is_success
            and isinstance(envelope, dict)
            and set(envelope) == {"result"}
            and isinstance(envelope["result"], dict)
        ):
            return envelope["result"]
        if isinstance(envelope, dict) and set(envelope) == {"error"}:
            fault = envelope["error"]
            if (
                isinstance(fault, dict)
                and set(fault)
                in ({"code", "message"}, {"code", "message", "tool_result"})
                and isinstance(fault["code"], str)
                and isinstance(fault["message"], str)
            ):
                result = fault.get("tool_result")
                if "tool_result" not in fault or (
                    isinstance(result, dict)
                    and set(result) == {"outcome", "diagnostics"}
                    and isinstance(result["outcome"], str)
                    and result["outcome"] in {"rejected", "failed"}
                    and isinstance(result["diagnostics"], list)
                    and all(
                        isinstance(item, str) for item in result["diagnostics"]
                    )
                ):
                    raise ToolProtocolError(
                        fault["code"], fault["message"], result
                    )
        raise ToolProtocolError(
            "tool_runtime_failure", "Invalid Backend response"
        )

    async def _catalog(self):
        try:
            response = await self._http.get(
                "/tools", params={"instance_id": self.selection.instance_id}
            )
        except httpx2.HTTPError as error:
            raise ToolProtocolError(
                "tool_runtime_failure", "Backend unavailable"
            ) from error
        catalog = self._response(response)
        if (
            set(catalog) != {"tools", "blacklist"}
            or not isinstance(catalog["tools"], list)
            or not all(
                isinstance(tool, dict) and isinstance(tool.get("name"), str)
                for tool in catalog["tools"]
            )
            or len({tool["name"] for tool in catalog["tools"]})
            != len(catalog["tools"])
            or not isinstance(catalog["blacklist"], list)
            or not all(isinstance(name, str) for name in catalog["blacklist"])
            or len(set(catalog["blacklist"])) != len(catalog["blacklist"])
        ):
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend catalog"
            )
        canonical = {
            "tools": sorted(catalog["tools"], key=lambda tool: tool["name"]),
            "blacklist": sorted(catalog["blacklist"]),
        }
        return catalog, json.dumps(
            canonical,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    async def ensure_current(self):
        if not self.ready:
            raise ToolProtocolError(
                "tool_runtime_failure", "Backend unavailable"
            )
        _, digest = await self._catalog()
        if digest != self._catalog_digest:
            raise ToolProtocolError(
                "tool_registry_stale", "Tool registry changed"
            )

    async def call_tool(self, name, arguments, *, session_id=None, public_base_url=None,
                        asserted_project_root=None):
        if not self.ready:
            raise ToolProtocolError(
                "tool_runtime_failure", "Backend unavailable"
            )
        operation = asyncio.create_task(
            self._http.post(
                "/tools",
                json={
                    "name": name,
                    "arguments": arguments,
                    "instance_id": self.selection.instance_id,
                    "session_id": session_id,
                    "public_base_url": public_base_url,
                    "asserted_project_root": asserted_project_root,
                },
            )
        )
        try:
            response = await asyncio.shield(operation)
        except asyncio.CancelledError:
            await asyncio.gather(operation, return_exceptions=True)
            raise
        except httpx2.HTTPError as error:
            raise ToolProtocolError(
                "tool_runtime_failure", "Backend unavailable"
            ) from error
        result = self._response(response)
        if (
            set(result) != {"value", "text"}
            or not isinstance(result["value"], dict)
            or (
                result["text"] is not None
                and not isinstance(result["text"], str)
            )
        ):
            raise ToolProtocolError(
                "tool_runtime_failure", "Invalid Backend response"
            )
        return result

    async def close(self):
        if self._closed:
            return
        self._closed = True
        try:
            if self._http is not None:
                await self._http.aclose()
        finally:
            if self._process is not None:
                process = self._process
                if process.stdin is not None:
                    process.stdin.close()
                def reap():
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            process.kill()
                            process.wait()
                await asyncio.to_thread(reap)
            if self._directory is not None:
                self._directory.cleanup()
