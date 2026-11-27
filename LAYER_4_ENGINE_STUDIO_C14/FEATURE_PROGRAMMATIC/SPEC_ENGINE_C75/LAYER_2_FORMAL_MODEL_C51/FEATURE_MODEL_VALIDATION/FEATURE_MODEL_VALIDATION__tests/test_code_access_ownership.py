import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import build_code_access_ownership


def component(parent, source):
    return SimpleNamespace(parent=parent, source_path=source, fields={}, name='unused')


class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.control = self.root / 'control'
        for directory in ('control/ENGINE_C1/FEATURE_C2', 'ENGINE_C1/FEATURE/pkg_pkg1/sub',
                          'ENGINE_C1/bridge/GRAPH_C3'):
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        self.snapshot = SimpleNamespace(project={}, components={
            'C1': component('C00', 'one.md'),
            'C2': component('C1', 'ENGINE_C1/two.md'),
            'C3': component('C1', 'ENGINE_C1/three.md'),
            'C4': component('C1', 'ENGINE_C1/four.md'),
        }, packages={'pkg1': SimpleNamespace(component='C2', fields={})})
        self.paths = {'ENGINE_C1', 'ENGINE_C1/FEATURE', 'ENGINE_C1/FEATURE/pkg_pkg1',
                      'ENGINE_C1/FEATURE/pkg_pkg1/sub', 'ENGINE_C1/bridge',
                      'ENGINE_C1/bridge/GRAPH_C3'}

    def build(self):
        return build_code_access_ownership(self.root, self.control, self.snapshot, self.paths)

    def test_owner_hierarchy_and_lookup(self):
        result = self.build()
        self.assertEqual(result.entries['C2']['path'], 'ENGINE_C1/FEATURE')
        self.assertNotIn('C4', result.entries)
        self.assertEqual(result.owner('ENGINE_C1/bridge/GRAPH_C3/a.py')['id'], 'C3')
        self.assertEqual(result.owner('ENGINE_C1/FEATURE/pkg_pkg1', 'package')['id'], 'pkg1')
        sub = result.owner('ENGINE_C1/FEATURE/pkg_pkg1/sub/a.py')
        self.assertEqual((sub['id'], sub['parent']), ('ENGINE_C1/FEATURE/pkg_pkg1/sub', 'pkg1'))
        self.assertEqual(result.owner('ENGINE_C1/bridge/file.py')['parent'], 'C1')

    def test_component_alias_under_an_intermediate_realization_folder(self):
        control = self.control / 'ENGINE_C1' / 'GRAPH_C3'
        control.mkdir()
        self.paths.remove('ENGINE_C1/bridge/GRAPH_C3')
        self.paths.add('ENGINE_C1/bridge/GRAPH')
        result = self.build()
        self.assertEqual(result.owner('ENGINE_C1/bridge/GRAPH/api.py')['id'], 'C3')
        self.assertEqual(result.entries['C3']['parent'], 'C1')

    def test_spec_lens_finds_native_alias_and_rejects_ambiguity(self):
        self.snapshot.components['C2'].source_path = 'ENGINE_C1/_SPEC/two.md'
        (self.control / 'ENGINE_C1' / '_SPEC').mkdir()
        result = self.build()
        self.assertEqual(result.entries['C2']['path'], 'ENGINE_C1/FEATURE')
        (self.control / 'ENGINE_C1' / 'OTHER_C2').symlink_to('FEATURE_C2')
        self.assertEqual(self.build().entries['C2']['path'], 'ENGINE_C1/FEATURE')
        (self.control / 'ENGINE_C1' / 'OTHER_C2').unlink()
        (self.control / 'ENGINE_C1' / 'OTHER_C2').mkdir()
        with self.assertRaisesRegex(ValueError, 'Ambiguous native Component path'):
            self.build()

    def test_configured_tier_one_folder_finds_native_alias(self):
        from types import MappingProxyType

        layout = MappingProxyType({'0': '.', '1': '01_CUSTOM_ARCHITECTURE', '2+': '_{lens}/{sublenses}'})
        self.snapshot.project['parameters'] = {'project': MappingProxyType({
            'folder_layout': MappingProxyType({'active_spec_by_tier': layout})})}
        self.snapshot.components['C2'].source_path = 'ENGINE_C1/01_CUSTOM_ARCHITECTURE/two.md'
        (self.control / 'ENGINE_C1' / '01_CUSTOM_ARCHITECTURE').mkdir()
        self.assertEqual(self.build().entries['C2']['path'], 'ENGINE_C1/FEATURE')

    def test_ambiguous_and_missing_declared_paths_fail(self):
        (self.root / 'ENGINE_C1/FEATURE/other_pkg1').mkdir()
        with self.assertRaisesRegex(ValueError, 'Component Seed realization path'):
            self.build()
        (self.root / 'ENGINE_C1/FEATURE/other_pkg1').rmdir()
        (self.root / 'ENGINE_C1/FEATURE/pkg_pkg1').rename(self.root / 'ENGINE_C1/FEATURE/ordinary')
        with self.assertRaisesRegex(ValueError, 'Component Seed realization path'):
            self.build()

    def test_duplicate_component_id_paths_fail(self):
        self.paths.add('ENGINE_C1/other/GRAPH_C3')
        with self.assertRaisesRegex(ValueError, 'Ambiguous Component'):
            self.build()


if __name__ == '__main__':
    unittest.main()
