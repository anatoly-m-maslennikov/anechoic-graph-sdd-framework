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
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_header__pub import canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.native_update import (archive_spec_draft, archive_ticket, change_spec_status,
                                           change_ticket_status, direct_update)






from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle_route_support import LifecycleRouteSupport


class LifecycleRouteMatrix(LifecycleRouteSupport, unittest.TestCase):
    def test_ticket_situation_route_rejections(self):
        templates = ('task', 'epic', 'problem', 'question', 'code_spec_mismatch', 'opportunity',
                     'analysis_report', 'work_report', 'work_log', 'spec_proposal')
        for template in templates:
            for situation in ('new', 'current', 'draft', 'archived'):
                for contained in (False, True):
                    with self.subTest(family='TKT', template=template, situation=situation, contained=contained):
                        project = self.project()
                        container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                        status = {'current': 'in_queue', 'draft': 'draft', 'archived': 'archived'}.get(situation)
                        if status:
                            header = canonical_native_header({'identity': {'atom_id': 'AN-T-2'},
                                'context': {'container': container, 'template': template},
                                'state': {'status': status, 'version': 1, 'updated_at': '2026-01-01'}})
                            owner = project.control_root / '001_TICKETS/TASKS/AN-T-1-TASK--owner'
                            path = native_carrier_path(header, 'Example', project_root=project.control_root,
                                owner_directory=owner if contained else project.control_root,
                                owner_template='task' if contained else None)
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) +
                                            '---\n\n## Summary\n\nExample\n')
                        ref = 'AN-T-2' + ({'draft': '@1-draft', 'archived': '@1'}.get(situation, ''))
                        target = {'ref_id': ref, 'version': 1}
                        capture = capture_native(project)
                        self.assertFalse(capture.errors, capture.errors)
                        before = self.files(project)
                        calls = [
                            (change_spec_status, {'target': target, 'targetStatus': 'active'}),
                            (archive_spec_draft, {'target': target}),
                        ]
                        if situation != 'current':
                            calls.append((change_ticket_status, {'target': target, 'targetStatus': 'done'}))
                        if situation in ('draft', 'archived') or (situation == 'current' and template not in ('task', 'epic')):
                            calls.append((create_draft, {'sourceCurrent': target}))
                        if situation in ('new', 'archived') or template in ('task', 'epic', 'problem', 'question', 'code_spec_mismatch', 'opportunity'):
                            calls.append((direct_update, {'target': target, 'changes': {'body': '\n## Summary\n\nExample\n'}}))
                        if situation != 'draft' or template not in ('task', 'epic'):
                            calls.append((promote_draft, {'target': target, 'targetStatus': 'backlog'}))
                        self._assert_routes_rejected(calls, capture, project, before)

    def test_non_ticket_situation_rejects_ticket_routes(self):
        templates = [('SPEC', 'AN-S-2', template) for template in
                     (None, 'DECISION', 'PKG', 'POLICY', 'action', 'component_contract', 'component_manifest',
                      'project_goal', 'project_manifest', 'step', 'workflow', 'axiom', 'applicable_principle')]
        templates += [('PROJECT_CONFIG', 'AN-P-2', template) for template in ('action', 'step', 'workflow', None)]
        for family, atom_id, template in templates:
            for situation in ('new', 'current', 'draft', 'archived'):
                for contained in (False, True):
                    with self.subTest(family=family, template=template, situation=situation, contained=contained):
                        project = self.project()
                        container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                        status = {'current': 'active', 'draft': 'draft', 'archived': 'archived'}.get(situation)
                        if status and not (family == 'PROJECT_CONFIG' and template is None and situation != 'draft'):
                            context = {'container': container, 'template': template}
                            if family == 'SPEC':
                                context.update(lens='SPEC', tier=1)
                            if template is None:
                                context.pop('template')
                            header = canonical_native_header({'identity': {'atom_id': atom_id}, 'context': context,
                                'state': {'status': status, 'version': 1, 'updated_at': '2026-01-01'}})
                            owner = project.control_root / '001_TICKETS/TASKS/AN-T-1-TASK--owner'
                            path = native_carrier_path(header, 'Example', project_root=project.control_root,
                                owner_directory=owner if contained else project.control_root,
                                owner_template='task' if contained else None)
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) +
                                            '---\n\n## Summary\n\nExample\n')
                        ref = atom_id + ({'draft': '@1-draft', 'archived': '@1'}.get(situation, ''))
                        target = {'ref_id': ref, 'version': 1}
                        capture = capture_native(project)
                        self.assertFalse(capture.errors, capture.errors)
                        before = self.files(project)
                        calls = [(direct_update, {'target': target, 'changes': {'body': '\n## Summary\n\nExample\n'}}),
                                 (change_ticket_status, {'target': target, 'targetStatus': 'done'}),
                                 (archive_ticket, {'target': target})]
                        if family == 'PROJECT_CONFIG' or situation != 'current':
                            calls.append((change_spec_status, {'target': target, 'targetStatus': 'active'}))
                        if family == 'PROJECT_CONFIG' or situation != 'draft':
                            calls.append((archive_spec_draft, {'target': target}))
                        if situation != 'current':
                            calls.append((create_draft, {'sourceCurrent': target}))
                        if situation != 'draft':
                            calls.append((promote_draft, {'target': target, 'targetStatus': 'ready'}))
                        self._assert_routes_rejected(calls, capture, project, before)

    def _assert_routes_rejected(self, calls, capture, project, before):
        for operation, params in calls:
            with self.subTest(route=operation.__name__):
                kwargs = {'current_rows': capture.atoms}
                if operation is change_ticket_status:
                    kwargs['check_definition'] = lambda: None
                with self.assertRaises((InputError, SourceChanged)):
                    operation(project, params, **kwargs)
                self.assertEqual(before, self.files(project))
