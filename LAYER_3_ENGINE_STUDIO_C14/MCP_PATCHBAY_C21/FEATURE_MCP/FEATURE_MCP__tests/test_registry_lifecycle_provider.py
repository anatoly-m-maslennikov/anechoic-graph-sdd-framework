"""Check native lifecycle MCP responses and discovery."""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

MCP = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(MCP), str(MCP.parents[1] / 'FEATURE_PROGRAMMATIC' / 'FEATURE_TOOLS')]
from registry_lifecycle_provider import NativeLifecycleProvider  # noqa: E402


class NativeLifecycleProviderTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_returns_exact_saved_reference(self):
        draft = {'ref_id': 'AN-T-1@1-draft'}
        artifact = {'ref_id': 'AN-T-1'}
        cases = (
            ('atom_lifecycle_create_draft', 'savedDraft', draft, 'completed'),
            ('atom_lifecycle_update', 'savedDraft', draft, 'draft_created'),
            ('atom_lifecycle_promote_draft', 'artifact', artifact, 'completed'),
        )
        for name, field, saved, status in cases:
            with self.subTest(name=name):
                outcome = {'outcome': 'completed', field: saved}
                provider = NativeLifecycleProvider(SimpleNamespace(lifecycle=lambda *_: outcome))
                self.assertEqual(await provider.call(name, {}), {'status': status, field: saved})


class LifecycleRegistryExposureTests(unittest.TestCase):
    def test_generated_registry_exposes_all_lifecycle_tools(self):
        from tool_registry_assets import FEATURE_RELATIVE, read_inventory
        from registry_lifecycle_provider import tool_descriptors

        inventory = read_inventory(MCP)
        entry = next(item for item in inventory.providers if item.provider_id == 'lifecycle')
        self.assertEqual('tool_descriptors', entry.descriptor_factory)
        all_names = {tool.name for tool in tool_descriptors()}
        admitted = {'atom_lifecycle_archive', 'atom_lifecycle_change_status', 'atom_lifecycle_create_draft',
                    'atom_lifecycle_direct_update', 'atom_lifecycle_promote_draft', 'atom_lifecycle_update'}
        self.assertEqual(admitted, all_names)
        self.assertFalse(all_names & set(inventory.blacklist))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            feature = root / FEATURE_RELATIVE
            feature.mkdir(parents=True)
            for name in ('tool_providers.json', 'registry_lifecycle_provider.py', 'registry_workbench_provider.py',
                         'registry_release_command_provider.py'):
                shutil.copy2(MCP / name, feature / name)
            env = dict(os.environ)
            env['PYTHONPATH'] = os.pathsep.join((str(MCP), str(MCP.parents[1] / 'FEATURE_PROGRAMMATIC' / 'FEATURE_TOOLS'),
                                                  str(MCP.parents[1] / 'IWE_CONSOLE_C43'), str(MCP.parents[1] / "FEATURE_PROGRAMMATIC")))
            subprocess.run([sys.executable, str(MCP / 'generate_tool_registry.py'), '--package-root', str(root)],
                           env=env, check=True, capture_output=True, text=True)
            generated = json.loads((feature / 'tool_registry.json').read_text())
        lifecycle = next(item for item in generated['providers'] if item['provider_id'] == 'lifecycle')
        self.assertEqual(all_names, {tool['name'] for tool in lifecycle['tools']})
        self.assertEqual(all_names, set(generated['public_tools']) & all_names)
        create = next(tool for tool in lifecycle['tools'] if tool['name'] == 'atom_lifecycle_create_draft')
        self.assertEqual({'sourceCurrent', 'changes', 'newAtom'}, set(create['inputSchema']['properties']))


if __name__ == '__main__':
    unittest.main()
