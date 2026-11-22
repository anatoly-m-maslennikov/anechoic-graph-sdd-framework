"""Exercise two Projects through the real Beta shared coordinator and peers."""
import tempfile
from pathlib import Path
import unittest

import httpx2

from WORKBENCH_BACKEND_beta_C70.shared_host_config import load
from WORKBENCH_BACKEND_beta_C70.shared_runtime__pub import create_app
from test_project_admission import write_project


class SharedBetaTests(unittest.IsolatedAsyncioTestCase):
    async def test_two_projects_are_isolated_and_config_is_pinned(self):
        with tempfile.TemporaryDirectory(dir='/tmp') as temporary:
            root = Path(temporary).resolve()
            projects = root / 'projects'
            projects.mkdir()
            roots = []
            for name in ('alpha', 'beta'):
                project = projects / name
                project.mkdir()
                manifest = write_project(project)
                manifest.write_text(manifest.read_text().replace('Declare Anechoic', 'Declare ' + name))
                roots.append(project)
            settings = root / 'runtime.toml'
            settings.write_text(f'schema_version=1\n[shared_mcp]\nprojects_root="{projects}"\nhttp_port=8092\nmax_loaded_projects=2\n')
            app = create_app(load(settings))
            async with httpx2.AsyncClient(transport=httpx2.ASGITransport(app=app), base_url='http://test', timeout=180) as client:
                catalog = (await client.get('/tools')).json()['result']['tools']
                self.assertEqual(['query_run'], [tool['name'] for tool in catalog])
                self.assertIn('project_root', catalog[0]['inputSchema']['required'])
                results = []
                identities = []
                for project in roots:
                    selection = (await client.post('/selection', json={'project_root': str(project)})).json()
                    identities.append(selection['result']['instance_id'])
                    envelope = {'name': 'query_run', 'arguments': {'project_root': str(project),
                                'sql': 'SELECT summary FROM atoms'}, 'session_id': None, 'public_base_url': None}
                    reply = (await client.post('/tools', json=envelope)).json()
                    self.assertIn('result', reply, reply)
                    results.append(reply['result']['value']['rows'])
                self.assertNotEqual(identities[0], identities[1])
                self.assertIn(['Declare alpha'], results[0])
                self.assertIn(['Declare beta'], results[1])
                self.assertEqual('outside_project_root', (await client.post('/selection', json={'project_root': str(root)})).json()['error']['code'])
                link = projects / 'link'
                link.symlink_to(roots[0], target_is_directory=True)
                self.assertEqual('invalid_project_root', (await client.post('/selection', json={'project_root': str(link)})).json()['error']['code'])
                blocked = projects / 'blocked'
                blocked.mkdir()
                manifest = write_project(blocked)
                text = manifest.read_text().replace("prefix='AN'", "prefix='AN', parameters={'project_mcp': {'tool_blacklist': ['query_run']}}")
                manifest.write_text(text)
                envelope['arguments']['project_root'] = str(blocked)
                self.assertEqual('tool_unavailable', (await client.post('/tools', json=envelope)).json()['error']['code'])
                settings.write_text(settings.read_text().replace('8092', '8093'))
                self.assertEqual('host_configuration_stale', (await client.post('/selection', json={'project_root': str(roots[0])})).json()['error']['code'])


if __name__ == '__main__':
    unittest.main()
