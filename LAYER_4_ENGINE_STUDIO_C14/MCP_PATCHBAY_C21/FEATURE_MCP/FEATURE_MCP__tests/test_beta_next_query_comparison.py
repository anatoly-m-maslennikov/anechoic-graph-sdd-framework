"""Exercise the supervised Beta Next Web and MCP interfaces."""
import asyncio
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

import httpx2 as httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

ENGINE = Path(__file__).resolve().parents[3]
SQL = 'SELECT reference, "content.summary" FROM atoms ORDER BY reference'
EXPECTED = [["EX-S-1", "Declare Example"], ["EX-T-1", "Example task"]]


def project(root):
    control = root / "_anechoic_example"
    control.mkdir(parents=True)
    (control / "EX-S-1-PROJECT_MANIFEST--declare-example.md").write_text(
        "---\natom_family: SPEC\natom_id: EX-S-1\ncontainer:\n  component: C00\ntier: -1\n"
        "context:\n  template: project_manifest\n  lens: SPEC\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nDeclare Example\n\n"
        "## Claim\n\n### Formal Claim\n\n```python\n"
        "from anechoic.formal_claims import declare_entity\nfrom anechoic.model import ProjectManifest\n"
        "declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Example', prefix='EX'))\n```\n"
    )
    task = control / "001_TICKETS/TASKS/EX-T-1-TASK--example.md"
    task.parent.mkdir(parents=True)
    task.write_text(
        "---\natom_family: TKT\natom_id: EX-T-1\ncontainer:\n  component: C00\npriority: 2\n"
        "context:\n  template: task\nstate:\n  status: active\n  version: 1\n"
        "  updated_at: '2026-11-19T00:00:00Z'\n---\n\n## Summary\n\nExample task\n"
    )
    return task


class BetaComparison(unittest.IsolatedAsyncioTestCase):
    async def test_web_and_mcp_follow_project_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            await self.run_role(Path(directory).resolve() / "beta_next", "beta_next")

    async def run_role(self, root, role):
        task = project(root)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        child = ("import sys,uvicorn; from MCP_PATCHBAY_C21.FEATURE_MCP import http_server as h; "
                 "original=uvicorn.run; uvicorn.run=lambda app,**kw: original(app,**(kw | {'host':'127.0.0.1'})); "
                 f"h.PORT={port}; sys.exit(h.main(['--project-root',sys.argv[1],'--port','{port}']))")
        launcher = ("import os,sys; from pathlib import Path; "
                    "from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_supervisor import supervise_project; "
                    "sys.exit(supervise_project([sys.executable,'-B','-c',sys.argv[2],sys.argv[1]], "
                    "dict(os.environ),Path(sys.argv[1])))")
        env = {**os.environ, "PYTHONPATH": str(ENGINE), "ANECHOIC_RUNTIME_STACK": role,
               "PYTHONDONTWRITEBYTECODE": "1", "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY": os.environ.get(
                   "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY", str(ENGINE.parent / ".anechoic_tmp/workbench/extensions"))}
        start = time.monotonic()
        with tempfile.TemporaryFile(mode="w+") as log:
            proc = subprocess.Popen([sys.executable, "-B", "-c", launcher, str(root), child], env=env,
                                    stdout=subprocess.DEVNULL, stderr=log)
            try:
                async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", timeout=30) as http:
                    await self.ready(http, proc)
                    timings = {"startup": time.monotonic() - start}
                    async with streamable_http_client(f"http://127.0.0.1:{port}/anechoic/mcp", http_client=http) as streams:
                        async with ClientSession(*streams) as client:
                            await client.initialize()
                            result = await self.compare(http, client, task, timings)
                    print(f"{role} timings (seconds): {timings}", flush=True)
                    return result
            except BaseException:
                log.seek(0)
                print(log.read(), file=sys.stderr)
                raise
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()

    async def ready(self, http, proc):
        async with asyncio.timeout(90):
            while True:
                self.assertIsNone(proc.poll(), "supervisor exited before readiness")
                try:
                    response = await http.get('/anechoic/health')
                    if response.status_code == 200 and response.json().get("state") == "ready":
                        return
                except httpx.ConnectError:
                    pass
                await asyncio.sleep(.2)

    async def compare(self, http, client, task, timings):
        async def read():
            before = time.monotonic()
            web = await http.post('/anechoic/Example/api/run', json={"sql": SQL, "result_delivery": "inline"})
            web.raise_for_status()
            timings.setdefault('web', []).append(time.monotonic() - before)
            before = time.monotonic()
            mcp = await client.call_tool('query_run', {"sql": SQL, "result_delivery": "inline"})
            self.assertFalse(mcp.is_error, mcp.structured_content)
            timings.setdefault('mcp', []).append(time.monotonic() - before)
            return web.json()['rows'], mcp.structured_content['rows']
        initial = await read()
        self.assertEqual((EXPECTED, EXPECTED), initial)
        task.write_text(task.read_text().replace('Example task', 'Changed task'))
        changed = [EXPECTED[0], ["EX-T-1", "Changed task"]]
        refresh_start = time.monotonic()
        async with asyncio.timeout(30):
            while True:
                final = await read()
                if final == (changed, changed):
                    break
                await asyncio.sleep(.2)
        timings['refresh'] = time.monotonic() - refresh_start
        return initial, final


if __name__ == '__main__':
    unittest.main()
