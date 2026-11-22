"""Project-local state and endpoint-only mount declaration, without Docker."""
import json
from pathlib import Path
import unittest

import yaml

APP = Path(__file__).resolve().parents[1]


class ProjectStateTests(unittest.TestCase):

    def test_compose_mount_and_resource_boundary_is_mcp_only(self):
        spec = yaml.safe_load((APP / 'docker/project-mcp.compose.yaml').read_text())
        self.assertEqual({'mcp-http'}, set(spec['services']))
        service = spec['services']['mcp-http']
        self.assertEqual('420s', service['healthcheck']['start_period'])
        self.assertIn('http://127.0.0.1:8092/anechoic/health', service['healthcheck']['test'][-1])
        self.assertEqual(['mcp-http'], service['command'])
        self.assertEqual(['127.0.0.1:${ANECHOIC_MCP_HTTP_PORT:?Project Settings HTTP port is required}:8092'], service['ports'])
        self.assertEqual([{'type': 'bind', 'source': '${ANECHOIC_PROJECT_ROOT}',
                          'target': '/project'}], service['volumes'])
        self.assertTrue(service['read_only'])
        self.assertEqual('no', service['restart'])
        self.assertEqual(['/tmp:size=128m,mode=1777'], service['tmpfs'])
        self.assertEqual('1536m', service['mem_limit'])
        self.assertEqual(1, service['cpus'])
        self.assertNotIn('CODEX_AUTHFILE', service['environment'])
        self.assertNotIn('worker', json.dumps(spec))
        self.assertNotIn('docker.sock', json.dumps(spec))


if __name__ == '__main__':
    unittest.main()
