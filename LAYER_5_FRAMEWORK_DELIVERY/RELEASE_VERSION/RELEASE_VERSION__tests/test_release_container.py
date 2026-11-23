"""Production container startup and ownership checks."""

import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest

from RELEASE_VERSION.release_container import start_container
from RELEASE_VERSION.release_assets import LocalReleaseError


class ContainerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path('/project-root')
        self.selection = SimpleNamespace(root=self.root, control_relative=Path('.anechoic'), instance_id='a' * 64)
        self.image = 'sha256:' + 'b' * 64
        self.fingerprint = 'c' * 64
        self.identifier = 'd' * 64
        self.calls = []
        self.row = {
            'Id': self.identifier, 'Image': self.image,
            'State': {'Running': True, 'Health': {'Status': 'healthy'}},
            'Config': {'Labels': {'org.anechoic.project': self.selection.instance_id,
                                  'org.anechoic.runtime.fingerprint': self.fingerprint,
                                  'org.anechoic.service': 'mcp-http',
                                  'org.anechoic.control_root': '.anechoic',
                                  'org.anechoic.host_project_root': str(self.root)}},
            'NetworkSettings': {'Ports': {'8092/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '18092'}]}},
            'Mounts': [{'Type': 'volume', 'Name': 'anechoic-framework-db', 'Destination': '/var/lib/anechoic', 'RW': True}, {'Type': 'bind', 'Source': str(self.root), 'Destination': '/project', 'RW': True}],
        }

    def run_docker(self, argv, root):
        self.calls.append(argv)
        self.assertEqual(root, self.root)
        output = self.identifier if argv[1] == 'run' else json.dumps(self.row) if argv[2] == 'inspect' else ''
        return subprocess.CompletedProcess(argv, 0, output, '')

    def start(self):
        return start_container(self.root, self.selection, self.image, self.fingerprint, 18092, self.run_docker)

    def test_healthy_owned_container(self):
        self.assertEqual('http://127.0.0.1:18092/anechoic/mcp', self.start())
        command = self.calls[0]
        self.assertIn('127.0.0.1:18092:8092', command)
        self.assertIn('--read-only', command)
        self.assertIn('type=volume,src=anechoic-framework-db,dst=/var/lib/anechoic', command)
        self.assertIn('ANECHOIC_FRAMEWORK_DB_ROOT=/var/lib/anechoic', command)
        self.assertIn('ANECHOIC_MCP_HTTP_HEALTHCHECK=1', command)
        self.assertEqual(command[-2:], (self.image, 'mcp-http'))
        self.assertEqual(len(self.calls), 2)

    def test_wrong_image_or_binding_cleans_only_candidate(self):
        for field in ('image', 'binding'):
            with self.subTest(field=field):
                self.setUp()
                if field == 'image':
                    self.row['Image'] = 'sha256:' + 'e' * 64
                else:
                    self.row['NetworkSettings']['Ports']['8092/tcp'][0]['HostIp'] = '0.0.0.0'
                with self.assertRaises(LocalReleaseError):
                    self.start()
                self.assertEqual(self.calls[-1], ('docker', 'container', 'rm', '-f', self.identifier))

    def test_missing_framework_volume_rejects_container(self):
        self.row['Mounts'] = self.row['Mounts'][1:]
        with self.assertRaises(LocalReleaseError):
            self.start()
        self.assertEqual(self.calls[-1], ('docker', 'container', 'rm', '-f', self.identifier))

    def test_reused_container_is_verified_and_never_removed_on_failure(self):
        self.row['Image'] = 'sha256:' + 'e' * 64
        with self.assertRaises(LocalReleaseError):
            start_container(self.root, self.selection, self.image, self.fingerprint, 18092,
                            self.run_docker, existing_container=self.identifier)
        self.assertEqual([('docker', 'container', 'inspect', '--format', '{{json .}}', self.identifier)],
                         self.calls)

    def test_invalid_input_runs_no_docker(self):
        with self.assertRaises(LocalReleaseError):
            start_container(self.root, self.selection, 'latest', self.fingerprint, 18092, self.run_docker)
        self.assertEqual([], self.calls)


if __name__ == '__main__':
    unittest.main()
