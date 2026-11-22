"""Default single-Project MCP and web calls share a separate Backend process."""

import asyncio
from dataclasses import replace
import json
import os
from pathlib import Path
import shutil
import signal
import shlex
import sys
import tempfile
from threading import Event
import time
import unittest
from unittest.mock import patch

import httpx2
from mcp import types
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from starlette.applications import Starlette

MCP = Path(__file__).resolve().parents[1]
ROOT = MCP.parents[2]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"

from MCP_PATCHBAY_C21.FEATURE_MCP.direct_gateway import native_runtime_gateway  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.backend_client import BackendClient, ToolProtocolError  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.native_startup import select_runtime_project  # noqa: E402
from MCP_PATCHBAY_C21.FEATURE_MCP.workbench_web import routes  # noqa: E402

CONTROL = "_anechoic_anechoic"
QUERY = "SELECT 42 AS answer"


def _test_environment():
    return {"ANECHOIC_RUNTIME_NAMESPACE": "docker",
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
                str(ROOT / ".anechoic_tmp/workbench/extensions"),
            )}


def _project(root):
    """Copy the native compiler's minimal authored Project and ontology inputs."""
    control = root / CONTROL
    control.mkdir()
    source = ROOT / CONTROL
    for name in ("AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md",
                 "AN-S-3039-SPEC-COMPONENT_MANIFEST--declare-engine-studio.md",
                 "AN-S-3040-SPEC-COMPONENT_MANIFEST--declare-meta-ontology.md"):
        shutil.copyfile(source / name, control / name)
    manifest = control / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
    raw = manifest.read_text(encoding="utf-8")
    assert "'storage': 'disk'" in raw and "'journal': {'storage': 'duckdb'}" in raw
    manifest.write_text(raw.replace("'storage': 'disk'", "'storage': 'memory'")
                        .replace("'journal': {'storage': 'duckdb'}", "'journal': {'storage': 'files'}"),
                        encoding="utf-8")
    ontology = "LAYER_1_META_ONTOLOGY_C9"
    (control / ontology).mkdir()
    (control / "LAYER_3_ENGINE_STUDIO_C14").mkdir()
    for path in (source / ontology).glob("AN-S-*-SPEC--*.md"):
        shutil.copyfile(path, control / ontology / path.name)
    selected = select_runtime_project(root, CONTROL)
    for relative in selected.parameters["runtime"]["workbench"]["import_graph"].get("python_roots", ()):
        (root / relative).mkdir(parents=True, exist_ok=True)


def _release_claim(root):
    directory = root / CONTROL / "002_PROJECT_CONFIG"
    directory.mkdir()
    name = "AN-P-58-WORKFLOW--release-a-selected-framework-version.md"
    claim = directory / name
    shutil.copyfile(ROOT / CONTROL / "002_PROJECT_CONFIG" / name, claim)
    script = root / "LAYER_5_FRAMEWORK_DELIVERY/release.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("# fixture; never executed\n", encoding="utf-8")
    return claim, script


async def _gateway_process(root):
    """Exercise the HTTP route in the very gateway that serves MCP stdio."""
    selection = select_runtime_project(root, CONTROL)
    with native_runtime_gateway(selection) as gateway:
        try:
            await gateway.initialize()
            app = Starlette(routes=routes(gateway))
            async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app),
                                          base_url="http://127.0.0.1") as client:
                invalid = await client.post("/anechoic/Anechoic/api/run", json={
                    "sql": QUERY, "name": "without-save",
                })
                response = await client.post("/anechoic/Anechoic/api/run", json={
                    "sql": QUERY, "result_delivery": "inline",
                })
            rejected_method = await asyncio.to_thread(_raw_method_reply, gateway._native_query)
            (root / "gateway-probe.json").write_text(json.dumps({
                "gateway_pid": os.getpid(), "backend_pid": gateway._native_query.backend_pid,
                "kernel_pid": _kernel_pid(gateway._native_query),
                "http_status": response.status_code, "http_body": response.json(),
                "invalid_status": invalid.status_code, "invalid_body": invalid.json(),
                "rejected_method": rejected_method,
            }), encoding="utf-8")
            await gateway.serve()
        finally:
            await gateway.close()


def _raw_method_reply(owner):
    return owner._http.post("/workbench", json={
        "operation": "run", "name": "query_run", "arguments": {"sql": QUERY},
        "instance_id": owner.selection.instance_id, "session_id": None,
    }).json()


def _kernel_pid(owner):
    response = owner._http.get("/health", timeout=2)
    response.raise_for_status()
    health = response.json()
    pid = health["kernel_pid"]
    if (health["pid"] != owner.backend_pid or health["instance_id"] != owner.selection.instance_id
            or type(pid) is not int or pid <= 1 or pid in {owner.backend_pid, os.getpid()}):
        raise AssertionError("Kernel PID is outside the admitted Backend binding")
    return pid


def _assert_process_stopped(test, pid):
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    test.fail("Backend process survived gateway shutdown")


async def _assert_lifecycle_projection(test, client, root):
    created = await client.call_tool("atom_lifecycle_create_draft", {"newAtom": {
        "template": "component_contract", "container": {"component": "C14"}, "lens": "SPEC",
        "body": "## Summary\n\nVerify Backend lifecycle\n\n## Guarantee\n\nReturn the result.\n",
    }})
    payload = created.structured_content
    test.assertEqual("completed", payload["status"], payload)
    draft = payload["savedDraft"]
    test.assertTrue((root / draft["path"]).is_file())
    visible = await client.call_tool("query_run", {
        "sql": "SELECT exact_ref FROM native_references WHERE exact_ref = '" + draft["ref_id"] + "'",
        "result_delivery": "inline",
    })
    test.assertFalse(visible.is_error, visible.structured_content)
    test.assertEqual([[draft["ref_id"]]], visible.structured_content["rows"])


class ApiBackendProcessTests(unittest.IsolatedAsyncioTestCase):
    async def test_backend_exit_preserves_unavailable_error(self):
        await self._assert_process_failure(kernel_exits=False)

    async def test_kernel_exit_preserves_unavailable_error(self):
        await self._assert_process_failure(kernel_exits=True)

    async def _assert_process_failure(self, *, kernel_exits):
        with (tempfile.TemporaryDirectory() as temporary,
              patch.dict(os.environ, _test_environment())):
            root = Path(temporary).resolve()
            _project(root)
            with native_runtime_gateway(select_runtime_project(root, CONTROL)) as gateway:
                try:
                    await gateway.initialize()
                    process = gateway._native_query._process
                    kernel = _kernel_pid(gateway._native_query)
                    os.kill(kernel if kernel_exits else process.pid, signal.SIGTERM)
                    await asyncio.to_thread(process.wait, 15)
                    self.assertFalse(gateway.ready)
                    with self.assertRaises(ToolProtocolError) as caught:
                        await gateway.workbench.call_tool("query_schema", {})
                    self.assertEqual("tool_runtime_failure", caught.exception.code)
                finally:
                    await gateway.close()
                _assert_process_stopped(self, kernel)

    async def test_cancelled_startup_reaps_child_before_returning(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _project(root)
            await self._cancel_startup(select_runtime_project(root, CONTROL))

    async def _cancel_startup(self, selection):
        entered, release = Event(), Event()
        start = BackendClient.start

        def paused_start(owner):
            entered.set()
            release.wait(timeout=30)
            start(owner)

        with (patch.dict(os.environ, _test_environment()),
              patch.object(BackendClient, "start", paused_start),
              native_runtime_gateway(selection) as gateway):
            pending = asyncio.create_task(gateway.initialize())
            try:
                self.assertTrue(await asyncio.to_thread(entered.wait, 5))
                owner = gateway._native_query
                pending.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await pending
                self.assertIsNotNone(owner._process.returncode)
                self.assertFalse(gateway.ready)
            finally:
                release.set()

    async def test_backend_refuses_a_changed_manifest_pin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _project(root)
            selection = replace(select_runtime_project(root, CONTROL), manifest_sha256="0" * 64)
            with native_runtime_gateway(selection) as gateway:
                with self.assertRaisesRegex(RuntimeError, "Backend did not start"):
                    await gateway.initialize()
                self.assertFalse(gateway.ready)
                self.assertEqual(1, gateway._native_query._process.returncode)

    async def test_backend_release_command_requires_manifest_enablement(self):
        with (tempfile.TemporaryDirectory() as temporary,
              patch.dict(os.environ, _test_environment())):
            root = Path(temporary).resolve()
            _project(root)
            _release_claim(root)
            manifest = root / CONTROL / "AN-S-3037-SPEC-PROJECT_MANIFEST--declare-anechoic.md"
            original = manifest.read_text(encoding="utf-8")
            self.assertIn("'release_workflows_enabled': True", original)
            manifest.write_text(original.replace("'release_workflows_enabled': True",
                                                 "'release_workflows_enabled': False"), encoding="utf-8")
            selection = select_runtime_project(root, CONTROL)
            self.assertFalse(selection.release_workflows_enabled)
            with native_runtime_gateway(selection) as gateway:
                try:
                    await gateway.initialize()
                    self.assertNotIn("local_release_command", {tool.name for tool in gateway.tools})
                    with self.assertRaises(ToolProtocolError) as caught:
                        await gateway.workbench.call_tool("local_release_command", {"run_id": "smoke-1"})
                    self.assertEqual("tool_unavailable", caught.exception.code)
                finally:
                    await gateway.close()

    async def test_release_command_uses_backend_claim_and_rejects_stale_or_duplicate_inputs(self):
        with (tempfile.TemporaryDirectory() as temporary,
              patch.dict(os.environ, _test_environment())):
            root = Path(temporary).resolve() / "Project with spaces"
            root.mkdir()
            _project(root)
            claim, script = _release_claim(root)
            selection = select_runtime_project(root, CONTROL)
            self.assertTrue(selection.release_workflows_enabled)
            with native_runtime_gateway(selection) as gateway:
                try:
                    await gateway.initialize()
                    owner = gateway._native_query
                    self.assertNotEqual(os.getpid(), owner.backend_pid)
                    arguments = {"run_id": "smoke-1"}
                    direct = (await gateway.workbench.call_tool("local_release_command", arguments))["value"]
                    command = await gateway.call(None, types.CallToolRequestParams(
                        name="local_release_command", arguments={"run_id": "smoke-1"}))
                    self.assertFalse(command.is_error, command.structured_content)
                    self.assertEqual(direct, command.structured_content)
                    args = shlex.split(direct["command"])
                    self.assertEqual("UV_PROJECT_ENVIRONMENT=" + str(root / "LAYER_5_FRAMEWORK_DELIVERY/.venv-release"), args[0])
                    self.assertNotIn("--no-sync", args)
                    self.assertIn("-E", args)
                    self.assertEqual(str(root), command.structured_content["working_directory"])
                    self.assertEqual(["local", "--project-root", str(root), "--run-id", "smoke-1"],
                                     args[args.index(str(script)) + 1:])
                    duplicate = claim.with_name("AN-P-59-WORKFLOW--duplicate.md")
                    duplicate.write_bytes(claim.read_bytes().replace(b"AN-P-58", b"AN-P-59"))
                    with self.assertRaisesRegex(ToolProtocolError, "Expected one Active") as caught:
                        await gateway.workbench.call_tool("local_release_command", arguments)
                    self.assertEqual("value_error", caught.exception.code)
                    duplicate.unlink()
                    self.assertEqual(direct, (await gateway.workbench.call_tool("local_release_command", arguments))["value"])
                    manifest = selection.manifest_path
                    original = manifest.read_bytes()
                    manifest.write_bytes(original + b"\n")
                    with self.assertRaisesRegex(ToolProtocolError, "Project binding changed") as caught:
                        await gateway.workbench.call_tool("local_release_command", arguments)
                    self.assertEqual("value_error", caught.exception.code)
                    manifest.write_bytes(original)
                    self.assertEqual(direct, (await gateway.workbench.call_tool("local_release_command", arguments))["value"])
                finally:
                    await gateway.close()

    async def test_stdio_and_web_share_backend_and_shutdown(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            _project(root)
            parameters = StdioServerParameters(
                command=sys.executable, args=["-B", "-P", "-m", __name__, str(root)],
                env={**_test_environment(), "PYTHONPATH": str(MCP.parents[1])},
            )
            async with asyncio.timeout(90), stdio_client(parameters) as streams:
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    probe = json.loads((root / "gateway-probe.json").read_text(encoding="utf-8"))
                    self._assert_web_probe(probe)
                    refused = await client.call_tool("query_rebuild", {"target": "unknown_table"})
                    self.assertTrue(refused.is_error)
                    self.assertEqual(["query_error: Unknown Workbench rebuild target: 'unknown_table'"],
                                     refused.structured_content["diagnostics"])
                    reply = await client.call_tool("query_page", {
                        "query_id": probe["http_body"]["query_id"], "result_delivery": "inline",
                    })
                    self.assertFalse(reply.is_error, reply.structured_content)
                    self.assertEqual([[42]], reply.structured_content["rows"])
                    await _assert_lifecycle_projection(self, client, root)
            _assert_process_stopped(self, probe["backend_pid"])
            _assert_process_stopped(self, probe["kernel_pid"])

    def _assert_web_probe(self, probe):
        self.assertNotEqual(probe["gateway_pid"], probe["backend_pid"])
        self.assertIsInstance(probe["backend_pid"], int)
        self.assertNotIn(probe["kernel_pid"], {probe["backend_pid"], probe["gateway_pid"]})
        os.kill(probe["backend_pid"], 0)
        self.assertEqual(400, probe["invalid_status"], probe["invalid_body"])
        self.assertEqual({"error": "name is only valid when save is true"}, probe["invalid_body"])
        self.assertEqual("value_error", probe["rejected_method"]["error"]["code"])
        self.assertEqual(200, probe["http_status"], probe["http_body"])
        self.assertEqual([[42]], probe["http_body"]["rows"])


if __name__ == "__main__":
    asyncio.run(_gateway_process(Path(sys.argv[1]).resolve()))
