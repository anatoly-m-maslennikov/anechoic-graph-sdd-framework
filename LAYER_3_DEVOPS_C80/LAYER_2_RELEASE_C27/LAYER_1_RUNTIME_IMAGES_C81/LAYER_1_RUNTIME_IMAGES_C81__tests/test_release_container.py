"""Production container startup and ownership checks."""

from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import NonCallableMock, patch

from LAYER_1_RUNTIME_IMAGES_C81.LAYER_1_RUNTIME_IMAGES_C81__shared import verify_release_container
from LAYER_1_RUNTIME_IMAGES_C81.release_container import start_container
from LAYER_1_RUNTIME_IMAGES_C81.release_assets import LocalReleaseError


class ContainerTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(TemporaryDirectory())).resolve()
        self.selection = NonCallableMock(
            spec_set=["root", "control_relative", "instance_id"],
            root=self.root, control_relative=Path(".anechoic"),
            instance_id="a" * 64,
        )
        self.image = 'sha256:' + 'b' * 64
        self.fingerprint = 'c' * 64
        self.identifier = 'd' * 64
        self.calls = []
        self.logs = ''
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
        if argv[1] == 'logs':
            return subprocess.CompletedProcess(argv, 0, '', self.logs)
        output = self.identifier if argv[1] == 'run' else ''
        if argv[2] == 'inspect':
            output = json.dumps(self.row if argv[-2] == '{{json .}}' else self.diagnostic_row())
        return subprocess.CompletedProcess(argv, 0, output, '')

    def diagnostic_row(self):
        state = self.row['State']
        return {
            'id': self.row['Id'], 'labels': self.row['Config']['Labels'],
            'status': state.get('Status'), 'running': state['Running'], 'health': state['Health']['Status'],
            'oom_killed': state.get('OOMKilled'), 'exit_code': state.get('ExitCode'),
            'memory_limit_bytes': 1610612736, 'nano_cpus': 1000000000,
        }

    def stop_candidate(self):
        self.row['State'].update(Running=False, Status='exited', OOMKilled=True, ExitCode=137)
        self.row['HostConfig'] = {'PortBindings': self.row['NetworkSettings']['Ports']}

    def start(self, evidence=None):
        return start_container(self.root, self.selection, self.image, self.fingerprint, 18092, self.run_docker,
                               evidence=evidence)

    def test_healthy_owned_container(self):
        evidence = {}
        endpoint = self.start(evidence)
        self.assertEqual('http://127.0.0.1:18092/anechoic/mcp', endpoint)
        self.assertEqual({
            'container_id': self.identifier, 'image_id': self.image, 'fingerprint': self.fingerprint,
            'project_instance': self.selection.instance_id, 'project_root': str(self.root),
            'control_root': '.anechoic', 'port': 18092, 'endpoint': endpoint, 'readiness': 'healthy',
        }, evidence)
        command = self.calls[0]
        self.assertIn('127.0.0.1:18092:8092', command)
        self.assertIn('--read-only', command)
        self.assertIn('type=volume,src=anechoic-framework-db,dst=/var/lib/anechoic', command)
        self.assertIn('ANECHOIC_FRAMEWORK_DB_ROOT=/var/lib/anechoic', command)
        self.assertIn('ANECHOIC_MCP_HTTP_HEALTHCHECK=1', command)
        self.assertEqual(command[-2:], (self.image, 'mcp-http'))
        self.assertEqual(len(self.calls), 2)

    def test_direct_release_passes_valid_logging_level_and_rejects_invalid_level(self):
        with patch.dict(os.environ, {'ANECHOIC_LOG_LEVEL': 'DEBUG'}):
            self.start()
        self.assertIn('ANECHOIC_LOG_LEVEL=DEBUG', self.calls[0])
        self.calls.clear()
        with patch.dict(os.environ, {'ANECHOIC_LOG_LEVEL': 'debug'}), self.assertRaisesRegex(LocalReleaseError, 'invalid_log_level'):
            self.start()
        self.assertEqual([], self.calls)

    def test_wrong_image_or_binding_retains_unverified_candidate(self):
        for field in ('image', 'binding'):
            with self.subTest(field=field):
                self.setUp()
                if field == 'image':
                    self.row['Image'] = 'sha256:' + 'e' * 64
                else:
                    self.row['NetworkSettings']['Ports']['8092/tcp'][0]['HostIp'] = '0.0.0.0'
                with self.assertRaises(LocalReleaseError) as raised:
                    self.start()
                self.assertFalse(any(call[:3] == ('docker', 'container', 'rm') for call in self.calls))
                self.assertIn('exact delivery identity unverified', raised.exception.__notes__[-1])

    def test_missing_framework_volume_rejects_container(self):
        self.row['Mounts'] = self.row['Mounts'][1:]
        with self.assertRaises(LocalReleaseError):
            self.start()
        self.assertFalse(any(call[:3] == ('docker', 'container', 'rm') for call in self.calls))

    def test_reused_container_is_verified_and_never_removed_on_failure(self):
        self.stop_candidate()
        with self.assertRaisesRegex(LocalReleaseError, 'local-release-container-exited') as raised:
            verify_release_container(self.root, self.selection, self.image, self.fingerprint, 18092,
                                     self.identifier, self.run_docker)
        self.assertEqual(('docker', 'logs', '--tail', '20', self.identifier), self.calls[-1])
        self.assertFalse(any(call[:3] == ('docker', 'container', 'rm') for call in self.calls))
        self.assertIn('"oom_killed":true', raised.exception.__notes__[-1])

    def test_failed_candidate_notes_bounded_redacted_diagnostics_before_removal(self):
        self.stop_candidate()
        self.row['Config']['Env'] = ['TOKEN=never-store-this']
        event = json.dumps({'severity': 'ERROR', 'event': 'startup_failed',
                            'details': {'token': 'never-store-this'}, 'reason': 'never-store-this'})
        self.logs = '\n'.join([event] * 20 + ['unstructured never-store-this'])
        evidence = {}
        with self.assertRaisesRegex(LocalReleaseError, 'local-release-container-exited') as raised:
            self.start(evidence)
        self.assertEqual({}, evidence)
        self.assertIn(('docker', 'logs', '--tail', '20', self.identifier), self.calls[:-1])
        self.assertEqual(('docker', 'container', 'rm', '-f', self.identifier), self.calls[-1])
        note = raised.exception.__notes__[-1]
        self.assertNotIn('never-store-this', note)
        details = json.loads(note.removeprefix('Local Release startup diagnostics: '))
        self.assertEqual(18092, details['loopback_port'])
        self.assertEqual(self.identifier, details['container_id'])
        self.assertEqual(137, details['state']['exit_code'])
        self.assertTrue(details['state']['oom_killed'])
        self.assertEqual([{'severity': 'ERROR', 'event': 'startup_failed'}] * 10, details['recent_events'])

    def test_failed_adoption_with_wrong_owner_omits_container_logs(self):
        self.row['Config']['Labels']['org.anechoic.project'] = 'e' * 64
        with self.assertRaisesRegex(LocalReleaseError, 'local-release-container-identity-mismatch') as raised:
            start_container(self.root, self.selection, self.image, self.fingerprint, 18092,
                            self.run_docker, existing_container=self.identifier)
        self.assertEqual([('docker', 'container', 'inspect')] * 2, [call[:3] for call in self.calls])
        self.assertIn('container ownership unverified', raised.exception.__notes__[-1])

    def test_failed_port_binding_reports_only_safe_cause_and_requested_port(self):
        def docker(argv, root):
            return subprocess.CompletedProcess(argv, 125, '', 'bind: address already in use; never-store-this')

        with self.assertRaisesRegex(LocalReleaseError, 'local-release-container-command-failed') as raised:
            start_container(self.root, self.selection, self.image, self.fingerprint, 18092, docker)
        notes = '\n'.join(raised.exception.__notes__)
        self.assertIn('Docker could not bind the requested port.', notes)
        self.assertIn('"loopback_port":18092', notes)
        self.assertNotIn('never-store-this', notes)

    def test_failed_bind_reconciles_only_proven_stopped_run_candidate(self):
        run_id = 'failed-bind'
        label = 'org.anechoic.local_release_run'
        label_value = sha256(run_id.encode()).hexdigest()

        def docker(argv, root):
            if argv[1] == 'run':
                self.calls.append(argv)
                return subprocess.CompletedProcess(argv, 125, '', 'bind: address already in use')
            if argv[:3] == ('docker', 'container', 'ls'):
                self.calls.append(argv)
                self.assertIn(f'label={label}={label_value}', argv)
                return subprocess.CompletedProcess(argv, 0, self.identifier, '')
            return self.run_docker(argv, root)

        for mode in ('owned-created', 'wrong-owner', 'owned-running'):
            with self.subTest(mode=mode):
                self.setUp()
                labels = self.row['Config']['Labels']
                labels[label] = label_value if mode != 'wrong-owner' else 'e' * 64
                if mode != 'owned-running':
                    self.stop_candidate()
                    self.row['State']['Status'] = 'created'
                with self.assertRaises(LocalReleaseError):
                    start_container(self.root, self.selection, self.image, self.fingerprint, 18092,
                                    docker, run_id=run_id)
                removals = [call for call in self.calls if call[:3] == ('docker', 'container', 'rm')]
                if mode == 'owned-created':
                    self.assertIn(('docker', 'logs', '--tail', '20', self.identifier), self.calls[:-1])
                    self.assertEqual([('docker', 'container', 'rm', self.identifier)], removals)
                else:
                    self.assertEqual([], removals)

    def test_invalid_input_runs_no_docker(self):
        with self.assertRaises(LocalReleaseError):
            start_container(self.root, self.selection, 'latest', self.fingerprint, 18092, self.run_docker)
        self.assertEqual([], self.calls)


if __name__ == '__main__':
    unittest.main()
