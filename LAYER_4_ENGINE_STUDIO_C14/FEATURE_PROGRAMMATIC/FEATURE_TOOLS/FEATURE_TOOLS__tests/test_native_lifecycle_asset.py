from pathlib import Path
import sys
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as draft_tests
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import TICKET_DIRECTORY, capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_asset


class NativeAssetTests(unittest.TestCase):
    write = draft_tests.NativeDraftTests.write
    setUp = draft_tests.NativeDraftTests.setUp

    def test_detached_and_attached_assets_are_current(self):
        body = '\n## Summary\n\nEvidence report\n\n## Findings\n\nDone.\n'
        for container, expected in [({'component': 'C00'}, f'{TICKET_DIRECTORY}/ASSETS'),
                                    ({'atom': 'AN-T-1'}, '001_TICKETS/TASKS/AN-T-1-TASK--example/ASSETS')]:
            rows = capture_native(self.selection).atoms
            result = create_asset(self.selection, {'newAtom': {'template': 'analysis_report', 'body': body,
                                                               'container': container}}, current_rows=rows)
            path = self.root / result['artifact']['path']
            self.assertEqual(self.control / expected, path.parent)
            header = yaml.safe_load(path.read_text().split('---', 2)[1])
            self.assertEqual(('TKT', container, 'analysis_report', 'in_queue'),
                             (header['atom_family'], header['container'], header['context']['template'], header['state']['status']))
            self.assertTrue(path.read_text().endswith(body))
            self.assertFalse(capture_native(self.selection).errors)
        self.assertEqual('AN-T-3', result['artifact']['atom_id'])

    def test_default_detaches_and_invalid_inputs_do_not_write(self):
        body = '\n## Summary\n\nReport\n'
        before = {p: p.read_bytes() for p in self.control.rglob('*.md')}
        for values in ({'template': 'task', 'body': body},
                       {'template': 'work_log', 'body': body, 'container': {'atom': 'AN-T-99'}},
                       {'template': 'work_log', 'body': body, 'container': {'component': 'C01'}}):
            with self.assertRaises((InputError, SourceChanged)):
                create_asset(self.selection, {'newAtom': values}, current_rows=self.rows)
            self.assertEqual(before, {p: p.read_bytes() for p in self.control.rglob('*.md')})
        result = create_asset(self.selection, {'newAtom': {'template': 'work_log', 'body': body}}, current_rows=self.rows)
        self.assertEqual(self.control / TICKET_DIRECTORY / 'ASSETS', (self.root / result['artifact']['path']).parent)


if __name__ == '__main__':
    unittest.main()
