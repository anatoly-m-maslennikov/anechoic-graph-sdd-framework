import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / 'migrate_native_atom_headers.py'
spec = importlib.util.spec_from_file_location('migrate_native_atom_headers', SCRIPT)
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


class MigrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'source'
        self.source.mkdir()
        self.output = self.root / 'output'

    def carrier(self, path, atom_id, family='SPEC', status='active', version=1, tier=None,
                template=None, relations=None):
        structure = {'container': {'component': 'C1'}}
        context = {'lens': 'DES'} if family == 'SPEC' else {'template': template or 'task'}
        if tier is not None:
            structure['tier'] = tier
        if family == 'TKT':
            structure['priority'] = 2
        header = {'atom_family': family, 'atom_id': atom_id, 'structure': structure,
                  'context': context, 'state': {'status': status, 'version': version,
                                                'updated_at': '2026-11-21T00:00:00+00:00'}}
        if relations:
            header['relations'] = relations
        path = self.source / path
        path.parent.mkdir(parents=True, exist_ok=True)
        body = b'\r\n## Summary\r\n\r\nKeep this body.\r\n'
        path.write_bytes(b'---\n' + yaml.safe_dump(header, sort_keys=False).encode() + b'---\n' + body)
        return path, body

    def read_header(self, path):
        return yaml.safe_load(path.read_bytes().split(b'---\n', 2)[1])

    def test_ready_recovery_default_and_companion(self):
        ready, body = self.carrier('component/__DES/AN-S-1-DES--ready.md', 'AN-S-1', status='ready',
                                   relations={'REFERENCES': ['AN-S-42@3', 'AN-T-7@2-draft']})
        companion = ready.with_suffix('') / 'nested'
        companion.mkdir(parents=True)
        (companion / 'attachment.txt').write_text('asset')
        self.carrier('component/__DES/AN-S-2-DES--default.md', 'AN-S-2')
        receipt = migration.run(self.source, self.output, {'AN-S-1@1': 1})
        migrated = self.output / 'component/02_ready/AN-S-1-DES--ready.md'
        header = self.read_header(migrated)
        self.assertEqual(header['state']['status'], 'ready')
        self.assertEqual(header['tier'], 1)
        self.assertEqual(header['relations']['IS_REFERENCE'], ['AN-S-42@3', 'AN-T-7@2-draft'])
        self.assertTrue(migrated.read_bytes().endswith(body))
        self.assertEqual((migrated.with_suffix('') / 'nested/attachment.txt').read_text(), 'asset')
        default = self.output / 'component/AN-S-2-DES--default.md'
        self.assertEqual(self.read_header(default)['tier'], 2)
        records = {r['old_ref']: r for r in receipt['carriers']}
        self.assertEqual(records['AN-S-1@1']['tier_source'], 'recovered')
        self.assertEqual(records['AN-S-1@1']['new_ref'], 'AN-S-1@1')
        self.assertEqual(records['AN-S-2@1']['tier_source'], 'defaulted')

    def test_archive_and_ticket_statuses(self):
        self.carrier('component/099_archived/AN-S-3@5-DES--archive.md', 'AN-S-3', status='archived', version=5, tier=2)
        self.carrier('__TKT/TASKS/AN-T-4-TASK--task.md', 'AN-T-4', family='TKT')
        self.carrier('__TKT/ASSETS/done/AN-T-5-WORK_REPORT--report.md', 'AN-T-5', family='TKT',
                     status='done', template='work_report')
        migration.run(self.source, self.output, {})
        archive = self.output / 'component/09_archived/AN-S-3@5-DES--archive.md'
        self.assertEqual(self.read_header(archive)['state']['version'], 5)
        ticket = self.output / '001_TICKETS/TASKS/AN-T-4-TASK--task.md'
        self.assertEqual(self.read_header(ticket)['state']['status'], 'in_queue')
        asset = self.output / '001_TICKETS/ASSETS/08_complete/AN-T-5-WORK_REPORT--report.md'
        self.assertEqual(self.read_header(asset)['state']['status'], 'complete')

    def test_collision_has_no_output(self):
        self.carrier('component/__DES/AN-S-6-DES--same.md', 'AN-S-6', tier=1)
        (self.source / 'component/AN-S-6-DES--same.md').write_text('occupied')
        with self.assertRaisesRegex(ValueError, 'collision'):
            migration.run(self.source, self.output, {})
        self.assertFalse(self.output.exists())
        self.assertFalse((self.root / 'output.receipt.json').exists())


if __name__ == '__main__':
    unittest.main()
