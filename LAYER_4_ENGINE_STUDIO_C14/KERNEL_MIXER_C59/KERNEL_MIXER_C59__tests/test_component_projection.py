"""Check Component Manifest projection across the tier migration."""

from unittest import TestCase

import duckdb

from KERNEL_MIXER_C59.native_projection import _write_components


IDENTITY = """## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(
    component_id='C3', name='Example'))
```
"""


class ComponentProjectionTests(TestCase):
    def test_tier_one_identity_only_and_purpose(self):
        connection = duckdb.connect(':memory:')
        self.addCleanup(connection.close)
        def row(tier, body):
            return {'status_group': 'Current', 'tier': tier, 'id': 'AN-S-3',
                    'header_json': {'context': {'template': 'component_manifest',
                                                'lens': 'SPEC', 'container': {'component': 'C1'}}},
                    'content_markdown': body, '_exact_ref': 'AN-S-3@1', 'source_path': 'manifest.md'}

        _write_components(connection, [row(1, IDENTITY)])
        self.assertEqual([('C3', None, [])], connection.execute(
            'SELECT component_id, boundaries, purpose_refs FROM components').fetchall())
        _write_components(connection, [row(1, '## Purpose\n\nProvide a service.\n\n' + IDENTITY)])
        self.assertEqual([(['AN-S-3@1'],)], connection.execute(
            'SELECT purpose_refs FROM components').fetchall())
        legacy = IDENTITY.replace('## Component Identity', '## Formal manifest')
        for tier in (0, 4):
            _write_components(connection, [row(tier, legacy)])
            self.assertEqual([('C3',)], connection.execute(
                'SELECT component_id FROM components').fetchall())
        _write_components(connection, [row(1, IDENTITY + '\n## Component Contract\n\nGuarantee.\n')])
        self.assertTrue(connection.execute('SELECT has_contract FROM components').fetchone()[0])
        _write_components(connection, [row(1, IDENTITY)])
        self.assertFalse(connection.execute('SELECT has_contract FROM components').fetchone()[0])
        _write_components(connection, [row(4, IDENTITY)])
        self.assertEqual(0, connection.execute('SELECT count(*) FROM components').fetchone()[0])
