"""Run an isolated Beta Backend for one admitted request."""
import asyncio
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import httpx2

ENGINE = Path(__file__).resolve().parents[1]


async def run(selection, request):
    with TemporaryDirectory(prefix='anechoic-beta-project-', dir='/tmp') as tmp:
        sock = Path(tmp).resolve() / 'api.sock'
        args = [sys.executable, '-B', '-P', '-m', 'WORKBENCH_BACKEND_beta_C70.runtime__pub',
                '--socket', str(sock), '--instance-id', selection.instance_id,
                '--project-root', str(selection.root), '--control-root', selection.control_relative.as_posix(),
                '--manifest-path', selection.manifest_path.relative_to(selection.root).as_posix(),
                '--manifest-sha256', selection.manifest_sha256, '--project-prefix', selection.project_prefix]
        env = {k: v for k, v in os.environ.items() if k != 'PYTHONHOME'}
        env['PYTHONPATH'] = str(ENGINE)
        process = await asyncio.create_subprocess_exec(*args, cwd=ENGINE, env=env,
                                                      stdin=asyncio.subprocess.PIPE, stdout=sys.stderr)
        try:
            async with httpx2.AsyncClient(transport=httpx2.AsyncHTTPTransport(uds=str(sock)),
                                          base_url='http://private', timeout=125, trust_env=False) as http:
                async with asyncio.timeout(125):
                    while True:
                        if process.returncode is not None:
                            raise RuntimeError('Beta Backend exited during startup')
                        try:
                            response = await http.get('/health', timeout=.5)
                            health = response.json()
                            if (response.status_code != 200 or health.get('pid') != process.pid
                                    or health.get('instance_id') != selection.instance_id
                                    or health.get('manifest_sha256') != selection.manifest_sha256):
                                raise RuntimeError('Beta Backend binding mismatch')
                            break
                        except httpx2.TransportError:
                            await asyncio.sleep(.05)
                response = await http.post('/tools', json=request)
                result = response.json()
                if not isinstance(result, dict) or set(result) not in ({'result'}, {'error'}):
                    raise RuntimeError('Invalid Beta Backend response')
                return result
        finally:
            process.stdin.close()
            try:
                await asyncio.wait_for(process.wait(), 15)
            except TimeoutError:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), 5)
                except TimeoutError:
                    process.kill()
                    await process.wait()
