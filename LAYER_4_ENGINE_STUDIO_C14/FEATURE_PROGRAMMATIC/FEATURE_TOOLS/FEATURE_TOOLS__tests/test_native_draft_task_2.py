from pathlib import Path
import sys
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import TICKET_DIRECTORY, capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header



import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures


class NewNativeTaskTests(fixtures.NewNativeTaskTests, unittest.TestCase):
    def test_canonical_owner_template_is_authored_not_filename(self):
        _, header, body = self.path.read_text().split('---', 2)
        metadata = yaml.safe_load(header)
        metadata['context']['template'] = 'epic'
        self.path.write_text('---\n' + yaml.safe_dump(canonical_native_header(metadata), sort_keys=False) + '---' + body)
        self.new['newAtom']['container'] = {'atom': 'AN-T-1'}
        output = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', output['outcome'])
        result = promote_draft(self.selection,
            {'target': {'ref_id': output['savedDraft']['ref_id'], 'version': 1}, 'targetStatus': 'backlog'},
            current_rows=capture_native(self.selection).atoms)
        self.assertEqual('completed', result['outcome'])


    def test_epic_owner_is_checked_again_at_promotion(self):
        epic = self.write('001_TICKETS/TASKS/AN-T-10-EPIC--parent.md', 'AN-T-10', template='epic')
        self.new['newAtom']['container'] = {'atom': 'AN-T-10'}
        output = create_draft(self.selection, self.new, current_rows=capture_native(self.selection).atoms)
        ref = output['savedDraft']['ref_id']
        rows = capture_native(self.selection).atoms
        epic.write_bytes(epic.read_bytes() + b'changed')
        with self.assertRaises(SourceChanged):
            promote_draft(self.selection, {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'},
                          current_rows=rows)
        self.assertTrue((self.root / output['savedDraft']['path']).exists())


    def test_rejects_unselected_component_and_unknown_fields(self):
        self.new['newAtom']['container'] = {'component': 'C999'}
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)
        self.new['newAtom']['container'] = {'component': 'C00'}
        self.new['newAtom']['extra'] = 'x'
        with self.assertRaises(InputError):
            create_draft(self.selection, self.new, current_rows=self.rows)


    def test_first_promotion_rejects_stale_draft(self):
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'}
        rows = capture_native(self.selection).atoms
        draft = self.root / output['savedDraft']['path']
        draft.write_bytes(draft.read_bytes() + b'changed')
        with self.assertRaises(SourceChanged):
            promote_draft(self.selection, params, current_rows=rows)


    def test_retry_after_draft_cleanup_failure_is_guarded_and_idempotent(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import effects_module as effects
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        path = self.root / output['savedDraft']['path']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'}
        rows = capture_native(self.selection).atoms
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            failed = promote_draft(self.selection, params, current_rows=rows)
        self.assertEqual('failed', failed['outcome'])
        self.assertTrue(path.exists())
        rows = capture_native(self.selection).atoms
        with self.assertRaises(InputError):
            promote_draft(self.selection, {**params, 'targetStatus': 'done'}, current_rows=rows)
        result = promote_draft(self.selection, params, current_rows=rows)
        self.assertEqual('completed', result['outcome'])
        self.assertEqual(['remove'], [item['operation'] for item in result['effects']])
        self.assertFalse(path.exists())


    def test_retry_refuses_changed_published_body(self):
        from unittest.mock import patch
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import effects_module as effects
        output = create_draft(self.selection, self.new, current_rows=self.rows)
        ref = output['savedDraft']['ref_id']
        params = {'target': {'ref_id': ref, 'version': 1}, 'targetStatus': 'backlog'}
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft_promotion.effects.remove', return_value=effects.Result(errors=[{'code': 'injected'}])):
            failed = promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertEqual('failed', failed['outcome'])
        current = self.control / TICKET_DIRECTORY / 'TASKS/backlog/AN-T-2-TASK--create-a-task.md'
        current.write_bytes(current.read_bytes() + b'changed')
        with self.assertRaisesRegex(InputError, 'Published carrier differs from the Draft'):
            promote_draft(self.selection, params, current_rows=capture_native(self.selection).atoms)
        self.assertTrue((self.root / output['savedDraft']['path']).exists())


