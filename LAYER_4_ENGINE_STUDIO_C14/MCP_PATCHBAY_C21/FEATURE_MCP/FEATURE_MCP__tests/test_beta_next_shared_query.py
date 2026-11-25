"""Exercise shared beta_next Web and MCP queries for independent Projects."""
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest

import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from .test_beta_next_query_comparison import project

ENGINE = Path(__file__).resolve().parents[3]
SQL = 'SELECT reference, "content.summary" FROM atoms ORDER BY reference'


def launch(settings, port):
    child = ("import sys,uvicorn; from MCP_PATCHBAY_C21.FEATURE_MCP import shared_http_server as h; "
             "original=uvicorn.run; uvicorn.run=lambda app,**kw: original(app,**(kw | {'host':'127.0.0.1'})); "
             f"h.PORT={port}; sys.exit(h.main(['--host-settings',sys.argv[1]]))")
    supervisor = ("import os,sys; from MCP_PATCHBAY_C21.FEATURE_MCP.docker.shared_supervisor import supervise; "
                  "sys.exit(supervise([sys.executable,'-B','-c',sys.argv[2],sys.argv[1]],dict(os.environ),sys.argv[1]))")
    env = {**os.environ, 'PYTHONPATH': str(ENGINE), 'ANECHOIC_RUNTIME_STACK': 'beta_next',
           'PYTHONDONTWRITEBYTECODE': '1', 'ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY': os.environ.get(
               'ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY', str(ENGINE.parent / '.anechoic_tmp/workbench/extensions'))}
    log = tempfile.TemporaryFile(mode='w+')
    proc = subprocess.Popen([sys.executable, '-B', '-c', supervisor, str(settings), child], env=env,
                            stdout=subprocess.DEVNULL, stderr=log)
    return proc, log


class SharedProjectQueries(unittest.IsolatedAsyncioTestCase):
    async def test_independent_projects_and_refresh(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            projects = root / 'projects'
            first, second = projects / 'alpha', projects / 'beta'
            project(first)
            task = project(second)
            task.write_text(task.read_text().replace('Example task', 'Second task'))
            settings = root / 'host.toml'
            settings.write_text('schema_version=1\n[shared_mcp]\nprojects_root=' + json.dumps(str(projects)) +
                                '\nhttp_port=8092\n[project_defaults]\nworkbench_storage="memory"\n')
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            proc, log = launch(settings, port)
            try:
                await self.exercise(port, proc, first, second, task)
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
                log.close()

    async def exercise(self, port, proc, first, second, task):
        url = f'http://127.0.0.1:{port}'
        async with httpx2.AsyncClient(base_url=url, timeout=30, trust_env=False) as http:
            async with asyncio.timeout(90):
                while True:
                    self.assertIsNone(proc.poll(), 'shared supervisor exited')
                    try:
                        response = await http.get('/anechoic/health')
                        if response.status_code == 200 and response.json().get('state') == 'ready':
                            break
                    except httpx2.TransportError:
                        pass
                    await asyncio.sleep(.2)
            async with streamable_http_client(url + '/anechoic/mcp', http_client=http) as streams:
                async with ClientSession(*streams) as client:
                    await client.initialize()
                    await self.check_queries(http, client, first, second, task)

    async def query(self, http, client, root):
        arguments = {'sql': SQL, 'result_delivery': 'inline', 'project_root': str(root)}
        web = await http.post('/anechoic/Example/api/run', json=arguments)
        web.raise_for_status()
        mcp = await client.call_tool('query_run', arguments)
        self.assertFalse(mcp.is_error, mcp.structured_content)
        return web.json(), mcp.structured_content

    async def check_queries(self, http, client, first, second, task):
        first_results = await self.query(http, client, first)
        second_results = await self.query(http, client, second)
        first_rows = [['EX-S-1', 'Declare Example'], ['EX-T-1', 'Example task']]
        second_rows = [['EX-S-1', 'Declare Example'], ['EX-T-1', 'Second task']]
        for result in first_results:
            self.assertEqual(first_rows, result['rows'])
        for result in second_results:
            self.assertEqual(second_rows, result['rows'])
        self.assertNotEqual(first_results[1]['query_id'], second_results[1]['query_id'])
        task.write_text(task.read_text().replace('Second task', 'Changed second task'))
        second_rows[1][1] = 'Changed second task'
        async with asyncio.timeout(30):
            while True:
                results = await self.query(http, client, second)
                if all(result['rows'] == second_rows for result in results):
                    break
                await asyncio.sleep(.2)
        for result in await self.query(http, client, first):
            self.assertEqual(first_rows, result['rows'])


if __name__ == '__main__':
    unittest.main()
