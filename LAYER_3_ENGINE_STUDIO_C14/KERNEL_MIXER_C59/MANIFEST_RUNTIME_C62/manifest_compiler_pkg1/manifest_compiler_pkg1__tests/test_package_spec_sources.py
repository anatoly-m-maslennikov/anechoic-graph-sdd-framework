import copy
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14' / 'FEATURE_PROGRAMMATIC'),
                str(ROOT / 'LAYER_3_ENGINE_STUDIO_C14' / 'FEATURE_PROGRAMMATIC' / 'FEATURE_TOOLS')]
from LAYER_3_ENGINE_STUDIO_C14.KERNEL_MIXER_C59.MANIFEST_RUNTIME_C62.manifest_compiler_pkg1.package_spec_sources import read_package_spec  # noqa: E402
from VALIDATE_ATOMS.validate_atoms_workers.parsing import parse_carrier  # noqa: E402

PATH = Path('AN-S-123-SPEC-PKG--test.md')
HEADER = {'identity': {'atom_id': 'AN-S-123'},
          'context': {'container': {'component': 'C62'}, 'lens': 'SPEC', 'template': 'PKG', 'package_id': 'pkg1'},
          'state': {'status': 'active', 'version': 1}}
CANONICAL = {'atom_family': 'SPEC', 'atom_id': 'AN-S-123', 'structure': {'container': {'component': 'C62'}, 'tier': 1},
             'context': {'lens': 'SPEC', 'template': 'PKG'}, 'state': {'status': 'active', 'version': 1, 'updated_at': '2026-11-20T00:00:00Z'}}
PROSE = '## Purpose\n\nTest purpose.\n\n## Contract\n\nTest contract.\n'
FORMAL = '''## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import PackageSpec
declare_entity(entity_name="Package Spec", instance=PackageSpec(package_id="pkg1", purpose="Test purpose.", contract="Test contract.", boundaries={"code": {"imports": ["pkg2"]}}))
```
'''


class PackageSpecTests(unittest.TestCase):
    def read(self, body=PROSE, metadata=None, path=PATH, parent='C62'):
        return read_package_spec(path, SimpleNamespace(metadata=metadata or copy.deepcopy(HEADER), body=body), parent, 'AN')

    def test_live_prose_sources(self):
        control = ROOT.parent / 'native-control'
        if not control.is_dir():
            control = ROOT / '_anechoic_anechoic'
        root = control / 'LAYER_3_ENGINE_STUDIO_C14' / 'KERNEL_MIXER_C59' / 'MANIFEST_RUNTIME_C62'
        files = sorted(root.glob('*-SPEC-PKG--*.md'))
        self.assertTrue(files)
        for path in files:
            fields = read_package_spec(path, parse_carrier(path.read_bytes(), path), 'C62', 'AN')
            self.assertTrue(fields['purpose'] and fields['contract'])

    def test_prose_and_formal(self):
        self.assertEqual(self.read()['ref_id'], 'AN-S-123@1')
        self.assertEqual(self.read(PROSE + FORMAL)['boundaries'], {'code': {'imports': ['pkg2']}})
        with self.assertRaisesRegex(ValueError, 'differ'):
            self.read(PROSE.replace('Test purpose.', 'Other.') + FORMAL)
        with self.assertRaisesRegex(ValueError, 'ID differs'):
            self.read(FORMAL.replace('package_id="pkg1"', 'package_id="pkg2"'))
        with self.assertRaisesRegex(ValueError, 'selectors'):
            self.read(FORMAL.replace('["pkg2"]', '["pkg2", "pkg2"]'))
        with self.assertRaisesRegex(ValueError, 'fields'):
            self.read('## Purpose\n\nOnly purpose.\n')

    def test_canonical_id_and_single_prose_sources(self):
        formal = FORMAL.replace(', purpose="Test purpose.", contract="Test contract."', '')
        fields = self.read(PROSE + formal, copy.deepcopy(CANONICAL))
        self.assertEqual(('pkg1', 'Test purpose.', 'Test contract.'),
                         (fields['package_id'], fields['purpose'], fields['contract']))
        with self.assertRaisesRegex(ValueError, 'only in sections'):
            self.read(PROSE + FORMAL, copy.deepcopy(CANONICAL))
        with self.assertRaisesRegex(ValueError, 'formal'):
            self.read(PROSE, copy.deepcopy(CANONICAL))

    def test_header_and_inactive(self):
        header = copy.deepcopy(HEADER)
        header['state']['status'] = 'draft'
        self.assertIsNone(self.read(metadata=header))
        header['state']['status'] = 'active'
        header['state']['version'] = True
        with self.assertRaisesRegex(ValueError, 'identity or parent'):
            self.read(metadata=header)
        with self.assertRaisesRegex(ValueError, 'identity or parent'):
            self.read(parent='C59')
        with self.assertRaisesRegex(ValueError, 'identity or parent'):
            self.read(path=Path('AN-S-123-SPEC-PKG--.md'))


if __name__ == '__main__':
    unittest.main()
