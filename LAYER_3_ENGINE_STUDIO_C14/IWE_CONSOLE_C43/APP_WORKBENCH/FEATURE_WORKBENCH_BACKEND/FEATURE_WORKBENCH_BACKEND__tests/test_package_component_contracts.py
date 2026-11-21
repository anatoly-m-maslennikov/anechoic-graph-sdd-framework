"""Component Contracts are audited against each Package's own exact pins."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import duckdb

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND import package_audit


class PackageComponentContractsTests(unittest.TestCase):
    def test_component_contracts_are_package_scoped_and_exact(self):
        def atom(ref, status='Current'):
            identity, version = ref.split('@')
            return {'ref': ref, '_exact_ref': ref, 'id': identity, 'status_group': status,
                    'source_path': f'UNIT_C1/__DES/{identity}-DES-COMPONENT_CONTRACT--report.md',
                    'header_json': {'atom_family': 'SPEC', 'atom_id': identity,
                                    'structure': {'container': {'component': 'C1'}, 'tier': 1},
                                    'context': {'template': 'component_contract', 'lens': 'DES'},
                                    'state': {'status': 'active' if status == 'Current' else 'archived',
                                              'version': int(version),
                                              'updated_at': '2026-11-19T00:00:00Z'}},
                    '_content_bytes': b'## Summary\n\nReport\n\n## Guarantee\n\nReturn the report.\n'}

        refs = ['AN-S-1@2', 'AN-S-2@1', 'AN-S-1@1']
        capture = SimpleNamespace(atoms=[atom(refs[0]), atom(refs[1]), atom(refs[2], 'Archived')],
                                  containment=[{'source_ref': ref, 'target_kind': 'Component', 'target_ref': 'C1'}
                                               for ref in refs])
        nodes = [('unit', 'package', None, 'unit', None, None, None),
                 ('child', 'package', None, 'unit/child', None, None, None)]
        selection = SimpleNamespace(structure_snapshot='snapshot', project_prefix='AN')
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
