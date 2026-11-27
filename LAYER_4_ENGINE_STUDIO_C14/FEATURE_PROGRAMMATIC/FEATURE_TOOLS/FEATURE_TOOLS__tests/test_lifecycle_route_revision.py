"""Generated native lifecycle paths; each case uses a fresh project."""
from pathlib import Path
import sys
import unittest


TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft, promote_draft







class NonTicketRevisionMatrix(unittest.TestCase):
    write = fixtures.NativeDraftTests.write
    spec = fixtures.NativeRevisionCarrierTests.spec

    def test_generic_spec_and_project_config_revision(self):
        for family in ('SPEC', 'PROJECT_CONFIG'):
            with self.subTest(family=family):
                fixtures.NativeRevisionCarrierTests.setUp(self)
                if family == 'SPEC':
                    path = self.spec('UNIT_C9/__DES/__DOM/AN-S-4-DOM--example.md', 'AN-S-4', 'DES/DOM')
                    atom_id, status = 'AN-S-4', 'ready'
                else:
                    path = self.write('002_PROJECT_CONFIG/AN-P-4-ACTION--example.md', 'AN-P-4', template='action')
                    atom_id, status = 'AN-P-4', 'active'
                rows = lambda: capture_native(self.selection).atoms
                original = path.read_bytes()
                revision = create_draft(self.selection, {'sourceCurrent': {'ref_id': atom_id, 'version': 1}},
                                        current_rows=rows())
                self.assertEqual('completed', revision['outcome'])
                draft = revision['savedDraft']
                self.assertEqual(original, path.read_bytes())
                result = promote_draft(self.selection,
                    {'target': {'ref_id': draft['ref_id'], 'version': 2}, 'targetStatus': status}, current_rows=rows())
                self.assertEqual('completed', result['outcome'], result)
                self.assertEqual(status, result['artifact']['status'])
                self.assertIn(atom_id + '@1', [row['_exact_ref'] for row in rows()])
                before = {p: p.read_bytes() for p in self.control.rglob('*.md')}
                with self.assertRaises((InputError, SourceChanged)):
                    create_draft(self.selection, {'sourceCurrent': {'ref_id': atom_id + '@1', 'version': 1}},
                                 current_rows=rows())
                self.assertEqual(before, {p: p.read_bytes() for p in self.control.rglob('*.md')})
