"""Component Contracts are audited against each Package's own exact pins."""
from unittest.mock import NonCallableMock
import json
import unittest
from unittest.mock import patch

import duckdb

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    NativeCapture,
)

from KERNEL_MIXER_C59 import package_audit


def _manifest_atom(ref, status='Current'):
    identity, version = ref.split('@')
    return {'ref': ref, '_exact_ref': ref, 'id': identity, 'status_group': status,
            'source_path': f'UNIT_C1/__SPEC/{identity}-SPEC-COMPONENT_MANIFEST--report.md',
            'tier': 1,
            'header_json': {'atom_family': 'SPEC', 'atom_id': identity,
                            'structure': {'container': {'component': 'C1'}, 'tier': 1},
                            'context': {'template': 'component_manifest', 'lens': 'SPEC'},
                            'state': {'status': 'active' if status == 'Current' else 'archived',
                                      'version': int(version),
                                      'updated_at': '2026-11-19T00:00:00Z'}},
            '_content_bytes': (b'## Component Identity\n\n```python\n'
                              b'from anechoic.formal_claims import declare_entity\n'
                              b'from anechoic.model import ComponentManifest\n'
                              b"declare_entity(entity_name='Component Manifest', "
                              b"instance=ComponentManifest(component_id='C1', name='Unit'))\n"
                              b'```\n\n## Component Contract\n\nReturn the report.\n')}


class PackageComponentContractsTests(unittest.TestCase):
    def test_component_contracts_are_package_scoped_and_exact(self):
        refs = ['AN-S-1@2', 'AN-S-2@1', 'AN-S-1@1']
        capture = NativeCapture(atoms=[_manifest_atom(refs[0]), _manifest_atom(refs[1]),
                                       _manifest_atom(refs[2], 'Archived')],
                                  containment=[{'source_ref': ref, 'target_kind': 'Component', 'target_ref': 'C1'}
                                               for ref in refs], errors={})
        nodes = [('unit', 'package', None, 'unit', None, None, None),
                 ('child', 'package', None, 'unit/child', None, None, None)]
        selection = NonCallableMock(
            spec_set=[
                'structure_snapshot', 'project_prefix'
            ],
            structure_snapshot='snapshot', project_prefix='AN')
        connection = duckdb.connect()
        self.addCleanup(connection.close)
        connection.execute('CREATE TABLE implementation_rmedo (owner_path VARCHAR, entry_kind VARCHAR, atom_id VARCHAR, version VARCHAR)')
        connection.executemany('INSERT INTO implementation_rmedo VALUES (?, ?, ?, ?)', [
            ('unit', 'implements', 'AN-S-1', '2'),
            ('unit', 'applies', 'AN-S-2', '1'),
            ('unit', 'implements', 'AN-S-1', '1'),
            ('unit/child', 'implements', 'AN-S-2', '1'),
        ])
        with patch.object(package_audit, 'read_structure'), \
             patch.object(package_audit, 'realization_component_paths', return_value={'unit': 'C1'}):
            package_audit.replace_package_audit(connection, selection, capture, nodes,
                                                {'unit': 'valid', 'unit/child': 'valid'}, tests=[])
        rows = dict(connection.execute('SELECT relative_path, component_contracts FROM package_audit').fetchall())
        self.assertEqual([{'ref': refs[0], 'covered': True}, {'ref': refs[1], 'covered': False}],
                         json.loads(rows['unit']))
        self.assertEqual([], json.loads(rows['unit/child']))

    def test_first_packages_below_code_free_component_and_nested_ownership(self):
        refs = ('AN-S-1@1', 'AN-S-2@1', 'AN-S-3@1')
        capture = NativeCapture(
            atoms=[{'ref': ref, 'status_group': 'Current', 'source_path': ref,
                    'header_json': {'context': {'template': 'component_contract'}},
                    '_content_bytes': b'body'} for ref in refs],
            containment=[{'source_ref': ref, 'target_kind': 'Component', 'target_ref': component}
                         for ref, component in zip(refs, ('C1', 'C2', 'C3'))],
            errors={},
        )
        paths = {'outer/feature', 'outer/other', 'outer/feature/child',
                 'outer/nested/feature', 'direct', 'direct/child'}
        components = {'outer': 'C1', 'outer/nested': 'C2', 'direct': 'C3'}
        selection = NonCallableMock(
            spec_set=[
                'structure_snapshot', 'project_prefix'
            ],
            structure_snapshot='snapshot', project_prefix='AN')
        with patch.object(package_audit, 'read_structure'), \
             patch.object(package_audit, 'realization_component_paths', return_value=components), \
             patch.object(package_audit, 'read_component_contract',
                          side_effect=lambda path, *args: {'ref_id': str(path)}):
            _, result = package_audit._contract_refs(selection, capture, paths)
        self.assertEqual([refs[0]], result['outer/feature'])
        self.assertEqual([refs[0]], result['outer/other'])
        self.assertNotIn('outer/feature/child', result)
        self.assertEqual([refs[1]], result['outer/nested/feature'])
        self.assertEqual([refs[2]], result['direct'])
        self.assertNotIn('direct/child', result)
