"""Generated native lifecycle paths; each case uses a fresh project."""
from pathlib import Path
import sys
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_source_rows__pub import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.common import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_asset import create_asset
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import native_carrier_path
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update import (archive_ticket, change_ticket_status, direct_update)






from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle_route_support import LifecycleRouteSupport


class LifecycleRouteMatrix(LifecycleRouteSupport, unittest.TestCase):
    def test_new_planning_ticket_paths(self):
        for template in ('task', 'epic'):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    project = self.project()
                    rows = lambda: capture_native(project).atoms
                    container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                    created = create_draft(project, {'newAtom': {'template': template, 'container': container,
                                          'body': '\n## Summary\n\nExample\n'}}, current_rows=rows())
                    self.assertEqual('completed', created['outcome'])
                    draft = created['savedDraft']
                    target = {'ref_id': draft['ref_id'], 'version': 1}
                    for forbidden in ('in_queue', 'done', 'in_progress'):
                        before = self.files(project)
                        with self.assertRaises(InputError):
                            promote_draft(project, {'target': target, 'targetStatus': forbidden}, current_rows=rows())
                        self.assertEqual(before, self.files(project))
                    published = promote_draft(project, {'target': target, 'targetStatus': 'backlog'}, current_rows=rows())
                    self.assertEqual('backlog', published['artifact']['status'])
                    target = {'ref_id': published['artifact']['ref_id'], 'version': 1}
                    for forbidden in ('done', 'in_progress'):
                        before = self.files(project)
                        with self.assertRaises(InputError):
                            change_ticket_status(project, {'target': target, 'targetStatus': forbidden},
                                                 current_rows=rows(), check_definition=lambda: None)
                        self.assertEqual(before, self.files(project))
                    for status in ('in_queue', 'done'):
                        result = change_ticket_status(project, {'target': target, 'targetStatus': status},
                                                      current_rows=rows(), check_definition=lambda: None)
                        self.assertEqual('completed', result['outcome'], result)
                        self.assertEqual(status, result['artifact']['status'])

    def test_revision_and_archived_routes(self):
        for template in ('task', 'epic'):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    project = self.project()
                    rows = lambda: capture_native(project).atoms
                    container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                    created = create_draft(project, {'newAtom': {'template': template, 'container': container,
                                          'body': '\n## Summary\n\nExample\n'}}, current_rows=rows())
                    draft = created['savedDraft']
                    first = promote_draft(project, {'target': {'ref_id': draft['ref_id'], 'version': 1},
                                          'targetStatus': 'backlog'}, current_rows=rows())
                    current = {'ref_id': first['artifact']['ref_id'], 'version': 1}
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        direct_update(project, {'target': current, 'changes': {'body': '\n## Summary\n\nExample\n'}},
                                      current_rows=rows())
                    self.assertEqual(before, self.files(project))
                    revision = create_draft(project, {'sourceCurrent': current}, current_rows=rows())
                    self.assertEqual('completed', revision['outcome'])
                    next_draft = revision['savedDraft']
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        archive_ticket(project, {'target': {'ref_id': next_draft['ref_id'], 'version': 2}},
                                       current_rows=rows())
                    self.assertEqual(before, self.files(project))
                    published = promote_draft(project, {'target': {'ref_id': next_draft['ref_id'], 'version': 2},
                                              'targetStatus': 'backlog'}, current_rows=rows())
                    self.assertEqual('completed', published['outcome'], published)
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        create_draft(project, {'sourceCurrent': {'ref_id': current['ref_id'] + '@1', 'version': 1}},
                                     current_rows=rows())
                    self.assertEqual(before, self.files(project))

    def test_issue_current_transitions_and_new_route_rejection(self):
        for template in ('problem', 'question', 'code_spec_mismatch', 'opportunity'):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    project = self.project()
                    rows = lambda: capture_native(project).atoms
                    container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        create_draft(project, {'newAtom': {'template': template, 'container': container,
                                     'body': '\n## Summary\n\nExample\n'}}, current_rows=rows())
                    self.assertEqual(before, self.files(project))
                    header = canonical_native_header({'identity': {'atom_id': 'AN-T-2'},
                              'context': {'container': container, 'template': template},
                              'state': {'status': 'backlog', 'version': 1, 'updated_at': '2026-01-01'}})
                    owner = project.control_root / '001_TICKETS/TASKS/AN-T-1-TASK--owner'
                    path = native_carrier_path(header, 'Example', project_root=project.control_root,
                                               owner_directory=owner if contained else project.control_root,
                                               owner_template='task' if contained else None)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) +
                                    '---\n\n## Summary\n\nExample\n')
                    target = {'ref_id': 'AN-T-2', 'version': 1}
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        archive_ticket(project, {'target': target}, current_rows=rows())
                    self.assertEqual(before, self.files(project))
                    for status in ('resolved', 'done', 'in_progress'):
                        before = self.files(project)
                        with self.assertRaises(InputError):
                            change_ticket_status(project, {'target': target, 'targetStatus': status},
                                                 current_rows=rows(), check_definition=lambda: None)
                        self.assertEqual(before, self.files(project))
                    for status in ('in_queue', 'resolved'):
                        result = change_ticket_status(project, {'target': target, 'targetStatus': status},
                                                      current_rows=rows(), check_definition=lambda: None)
                        self.assertEqual('completed', result['outcome'], result)
                        self.assertEqual(status, result['artifact']['status'])

    def test_pmeta_and_spec_reject_ticket_only_routes(self):
        for family, atom_id in (('PROJECT_CONFIG', 'AN-P-2'), ('SPEC', 'AN-S-2')):
            for contained in (False, True):
                with self.subTest(family=family, contained=contained):
                    project = self.project()
                    container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                    before = self.files(project)
                    for template in (family.lower(),):
                        with self.assertRaises(InputError):
                            create_asset(project, {'newAtom': {'template': template, 'container': container,
                                         'body': '\n## Summary\n\nExample\n'}},
                                         current_rows=capture_native(project).atoms)
                    for operation, params in ((direct_update, {'target': {'ref_id': atom_id, 'version': 1},
                                                               'changes': {'body': 'Example'}}),
                                              (archive_ticket, {'target': {'ref_id': atom_id, 'version': 1}})):
                        with self.assertRaises((InputError, SourceChanged)):
                            operation(project, params, current_rows=capture_native(project).atoms)
                    self.assertEqual(before, self.files(project))
