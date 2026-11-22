import copy
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[6]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.component_seed_manifest__pub import read_component_seed_manifest  # noqa: E402

PATH = Path('AN-S-123-SPEC--test.md')
HEADER = {'atom_family': 'SPEC', 'atom_id': 'AN-S-123', 'structure': {'container': {'component': 'C62'}, 'tier': 1},
          'context': {'lens': 'SPEC', 'template': 'component_seed_manifest'},
          'state': {'status': 'active', 'version': 1, 'updated_at': '2026-11-20T00:00:00Z'}}
BODY = '''# Example

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest
declare_entity(entity_name="Component Seed Manifest", instance=ComponentSeedManifest(component_seed_id="CS123", boundaries={"code": {"imports": ["CS124"]}}))
```

## Purpose

Test purpose.

## Solution

Test solution.
'''


class ComponentSeedManifestTests(unittest.TestCase):
    def read(self, body=BODY, metadata=None, parent='C62'):
        return read_component_seed_manifest(PATH, SimpleNamespace(metadata=metadata or copy.deepcopy(HEADER), body=body), parent, 'AN')

    def test_valid_manifest(self):
        fields = self.read()
        self.assertEqual((fields['ref_id'], fields['component_seed_id'], fields['purpose'], fields['solution']),
                         ('AN-S-123@1', 'CS123', 'Test purpose.', 'Test solution.'))
        self.assertEqual(fields['boundaries'], {'code': {'imports': ['CS124']}})

    def test_invalid_form_and_content(self):
        for body in [BODY + '\n## Purpose\nDuplicate\n', BODY + '\n## Extra\nExtra text\n',
                     BODY.replace('## Solution', '## Missing'),
                     BODY.replace('## Purpose', '## Solution', 1).replace('## Solution\n\nTest solution.', '## Purpose\n\nTest solution.'),
                     BODY.replace('Test solution.', ''), BODY.replace('CS123', 'CS123x'),
                     BODY.replace('component_seed_id="CS123"', 'component_seed_id="CS123", purpose="Test purpose."'),
                     BODY.replace('```python', '```text'), BODY.replace('## Formal Manifest', '### Formal Manifest'),
                     BODY.replace('## Purpose', '```python\npass\n```\n\n## Purpose'),
                     BODY.replace('["CS124"]', '["CS124", "CS124"]')]:
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.read(body)

    def test_header_and_inactive(self):
        header = copy.deepcopy(HEADER)
        header['state']['status'] = 'draft'
        self.assertIsNone(self.read(metadata=header))
        header['state']['status'] = 'active'
        header['state']['version'] = True
        with self.assertRaises(ValueError):
            self.read(metadata=header)
        with self.assertRaises(ValueError):
            self.read(parent='C59')


if __name__ == '__main__':
    unittest.main()
