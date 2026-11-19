"""Native Project startup keeps the host identity and Manifest port."""

from pathlib import Path
from dataclasses import replace
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parent
sys.path[:0] = [str(MCP / 'docker'), str(MCP), str(PROGRAMMATIC / 'FEATURE_TOOLS'), str(PROGRAMMATIC)]

from native_project_selection import rebind_native_selection
from native_startup import select_runtime_project
from project_mcp_backend import ProjectMcpBackend
from project_mcp_launcher import Launcher
from project_selection import ProjectSelectionError, _instance_id
from project_tool_context import native_arguments
from test_project_mcp_launcher_startup import Backend, healthy_row


class NativeHostLauncherTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / '.anechoic_anechoic'
        path = self.control / 'SPEC' / 'AN-S-001-PROJECT_MANIFEST--declare.md'
        path.parent.mkdir(parents=True)
        header = {'identity': {'atom_id': 'AN-S-001'},
                  'context': {'container': {'component': 'C00'}, 'tier': -1,
                              'template': 'project_manifest'},
                  'state': {'status': 'active', 'version': 1}}
        path.write_text(f'---\n{yaml.safe_dump(header)}---\n\n## Claim\n\n### Formal Claim\n\n```python\n'
                        'from anechoic.formal_claims import declare_entity\n'
                        'from anechoic.model import ProjectManifest\n'
                        'declare_entity(entity_name="Project Manifest", '
                        'instance=ProjectManifest(name="Anechoic", prefix="AN", '
                        'parameters={"project_mcp": {"http_port": 56318}}))\n```\n', encoding='utf-8')

    def test_launcher_selects_manifest_and_publishes_its_port(self):
        class HostBackend(Backend):
            def start(self, selection, image_id, fingerprint, timeout, port=None):
                super().start(selection, image_id, fingerprint, timeout, port)
                self.rows = [healthy_row(project=selection.instance_id, host_port=str(port))]

        backend = HostBackend()
        result = Launcher(backend=backend).launch(self.root, source_root=PROGRAMMATIC)
        selected = select_runtime_project(self.root)
        self.assertEqual(('READY_STARTED', 56318, str(self.control), selected.instance_id),
                         (result['condition'], result['port'], result['control_root'], result['project_id']))
        self.assertEqual([56318], backend.start_ports)
        self.assertEqual("anechoic-mcp-" + selected.instance_id[:24],
                         ProjectMcpBackend._compose_project(selected))
        environment = ProjectMcpBackend._environment(selected, result['image_id'], result['fingerprint'], 56318)
        self.assertEqual((str(self.root), self.control.name, selected.instance_id, '56318'),
                         (environment['ANECHOIC_PROJECT_ROOT'], environment['ANECHOIC_CONTROL_ROOT'],
                          environment['ANECHOIC_PROJECT_INSTANCE_ID'], environment['ANECHOIC_MCP_HTTP_PORT']))
        refused = Launcher(backend=backend).launch(self.root, source_root=PROGRAMMATIC, port=56317)
        self.assertEqual('PROJECT_SELECTION_REFUSED', refused['condition'])
        self.assertEqual(1, backend.start_calls)

    def test_invalid_manifest_port_refuses_before_runtime_effects(self):
        selection = select_runtime_project(self.root)
        for port in (None, True, 0, 65536, '56318'):
            with self.subTest(port=port):
                backend = Backend()
                invalid = replace(selection, parameters={'project_mcp': {'http_port': port}})
                with patch('project_mcp_launcher.resolve_project', return_value=invalid):
                    result = Launcher(backend=backend).launch(self.root, source_root=PROGRAMMATIC)
                self.assertEqual('PROJECT_SELECTION_REFUSED', result['condition'])
                self.assertEqual((0, 0), (backend.resolve_image_calls, backend.start_calls))

    def test_transport_checks_identity_and_accepts_only_bound_roots(self):
        selected = select_runtime_project(self.root)
        host = self.root.parent / 'unmounted-native-project'
        identity = _instance_id(host, selected.control_relative)
        transported = rebind_native_selection(selected, identity, host_root=host)
        for root in (self.root, host):
            self.assertEqual({'sql': 'select 1'}, native_arguments(
                {'project_root': str(root), 'sql': 'select 1'}, transported, self.root))
        with self.assertRaises(ValueError):
            native_arguments({'project_root': str(host.parent)}, transported, self.root)
        with self.assertRaises(ProjectSelectionError):
            rebind_native_selection(selected, 'a' * 64, host_root=host)
        alias = self.root.parent / (self.root.name + '-alias')
        alias.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(alias.unlink)
        with self.assertRaises(ProjectSelectionError):
            rebind_native_selection(selected, _instance_id(alias, selected.control_relative), host_root=alias)


if __name__ == '__main__':
    unittest.main()
