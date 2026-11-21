"""Generated native lifecycle paths; each case uses a fresh project."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native
from ATOM_LIFECYCLE.common import InputError, SourceChanged
from ATOM_LIFECYCLE.native_asset import create_asset
from native_carrier_header import canonical_native_header
from native_carrier_placement import native_carrier_path
import test_native_lifecycle_draft as fixtures
from ATOM_LIFECYCLE.native_draft import create_draft, promote_draft
from ATOM_LIFECYCLE.native_update import (archive_spec_draft, archive_ticket, change_spec_status,
                                           change_ticket_status, direct_update)


# Shared case dimensions for static and MCP lifecycle checks.  None is the
# admitted generic SPEC or template-free PMETA Draft, not a wildcard.
LIFECYCLE_TEMPLATES = {
    'TKT': ('task', 'epic', 'problem', 'question', 'code_spec_mismatch', 'opportunity',
            'analysis_report', 'work_report', 'work_log', 'spec_proposal'),
    'SPEC': (None, 'DECISION', 'PKG', 'POLICY', 'action', 'component_contract', 'component_manifest',
             'project_goal', 'project_manifest', 'step', 'workflow', 'axiom', 'applicable_principle'),
    'PMETA': ('action', 'step', 'workflow', None),
}
LIFECYCLE_ROUTES = ('create_draft', 'update', 'create_asset', 'direct_update',
                    'promote_draft', 'change_status', 'archive')


def lifecycle_cases():
    for family, templates in LIFECYCLE_TEMPLATES.items():
        for template in templates:
            for situation in ('new', 'current', 'draft', 'archived'):
                for contained in (False, True):
                    for route in LIFECYCLE_ROUTES:
                        yield {'route': route, 'family': family, 'template': template,
                               'situation': situation, 'contained': contained}


class LifecycleRouteMatrix(unittest.TestCase):
    def project(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (root / '.git').mkdir()
        control = root / '.anechoic_test'
        control.mkdir()
        manifest = control / 'AN-S-1-PROJECT_MANIFEST--manifest.md'
        owner = control / '001_TICKETS/TASKS/AN-T-1-TASK--owner.md'
        owner.parent.mkdir(parents=True)
        for path, identity, template in ((manifest, 'AN-S-1', 'project_manifest'),
                                          (owner, 'AN-T-1', 'task')):
            header = {'identity': {'atom_id': identity},
                      'context': {'container': {'component': 'C00'}, 'template': template},
                      'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'}}
            path.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nOwner\n')
        return SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                               manifest_sha256=sha256(manifest.read_bytes()).hexdigest(), project_prefix='AN')

    def files(self, project):
        return {p.relative_to(project.root): p.read_bytes() for p in project.control_root.rglob('*.md')}

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
        for family, atom_id in (('PMETA', 'AN-P-2'), ('SPEC', 'AN-S-2')):
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

    write = fixtures.NativeDraftTests.write

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
                        for operation, params in calls:
                            with self.subTest(route=operation.__name__):
                                kwargs = {'current_rows': capture.atoms}
                                if operation is change_ticket_status:
                                    kwargs['check_definition'] = lambda: None
                                with self.assertRaises((InputError, SourceChanged)):
                                    operation(project, params, **kwargs)
                                self.assertEqual(before, self.files(project))

    def test_non_ticket_situation_rejects_ticket_routes(self):
        templates = [('SPEC', 'AN-S-2', template) for template in
                     (None, 'DECISION', 'PKG', 'POLICY', 'action', 'component_contract', 'component_manifest',
                      'project_goal', 'project_manifest', 'step', 'workflow', 'axiom', 'applicable_principle')]
        templates += [('PMETA', 'AN-P-2', template) for template in ('action', 'step', 'workflow', None)]
        for family, atom_id, template in templates:
            for situation in ('new', 'current', 'draft', 'archived'):
                for contained in (False, True):
                    with self.subTest(family=family, template=template, situation=situation, contained=contained):
                        project = self.project()
                        container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                        status = {'current': 'active', 'draft': 'draft', 'archived': 'archived'}.get(situation)
                        if status and not (family == 'PMETA' and template is None and situation != 'draft'):
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
                        if family == 'PMETA' or situation != 'current':
                            calls.append((change_spec_status, {'target': target, 'targetStatus': 'active'}))
                        if family == 'PMETA' or situation != 'draft':
                            calls.append((archive_spec_draft, {'target': target}))
                        if situation != 'current':
                            calls.append((create_draft, {'sourceCurrent': target}))
                        if situation != 'draft':
                            calls.append((promote_draft, {'target': target, 'targetStatus': 'ready'}))
                        for operation, params in calls:
                            with self.subTest(route=operation.__name__):
                                kwargs = {'current_rows': capture.atoms}
                                if operation is change_ticket_status:
                                    kwargs['check_definition'] = lambda: None
                                with self.assertRaises((InputError, SourceChanged)):
                                    operation(project, params, **kwargs)
                                self.assertEqual(before, self.files(project))

    def test_flat_ticket_archive_requires_replacement(self):
        templates = ('task', 'epic', 'problem', 'question', 'code_spec_mismatch', 'opportunity',
                     'analysis_report', 'work_report', 'work_log', 'spec_proposal')
        for template in templates:
            for situation in ('current', 'draft'):
                with self.subTest(template=template, situation=situation):
                    project = self.project()
                    status = 'draft' if situation == 'draft' else 'in_queue'
                    header = canonical_native_header({'identity': {'atom_id': 'AN-T-2'},
                        'context': {'container': {'component': 'C00'}, 'template': template},
                        'state': {'status': status, 'version': 1, 'updated_at': '2026-01-01'}})
                    path = native_carrier_path(header, 'Example', project_root=project.control_root,
                                               owner_directory=project.control_root)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) + '---\n\n## Summary\n\nExample\n')
                    ref = 'AN-T-2@1-draft' if situation == 'draft' else 'AN-T-2'
                    target = {'ref_id': ref, 'version': 1}
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        archive_ticket(project, {'target': target}, current_rows=capture_native(project).atoms)
                    self.assertEqual(before, self.files(project))
                    replacement = canonical_native_header({'identity': {'atom_id': 'AN-T-3'},
                        'context': {'container': {'component': 'C00'}, 'template': 'task'},
                        'state': {'status': 'in_queue', 'version': 1, 'updated_at': '2026-01-01'},
                        'relations': {'IS_REPLACEMENT_FOR': ['AN-T-2']}})
                    replacement_path = native_carrier_path(replacement, 'Replacement', project_root=project.control_root,
                                                           owner_directory=project.control_root)
                    replacement_path.parent.mkdir(parents=True, exist_ok=True)
                    replacement_path.write_text('---\n' + yaml.safe_dump(replacement, sort_keys=False) +
                                                '---\n\n## Summary\n\nReplacement\n')
                    outcome = archive_ticket(project, {'target': target}, current_rows=capture_native(project).atoms)
                    self.assertEqual('completed', outcome['outcome'], outcome)
                    self.assertEqual('AN-T-2@1', outcome['artifact']['ref_id'])
                    self.assertFalse(path.exists())

    def test_project_spec_templates_and_draft_archive(self):
        for template in ('axiom', 'applicable_principle'):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    fixtures.NativeRevisionCarrierTests.setUp(self)
                    project = self.selection
                    project.manifest_path.write_text(project.manifest_path.read_text().replace('component: C0}', 'component: C00}'))
                    project.manifest_sha256 = sha256(project.manifest_path.read_bytes()).hexdigest()
                    rows = lambda: capture_native(project).atoms
                    calls = []
                    def validate(kind, header, component):
                        calls.append((kind, component))
                    values = {'template': template, 'container': {'atom': 'AN-T-1'} if contained else {'component': 'C00'},
                              'lens': 'SPEC', 'body': '\n## Summary\n\nExample\n'}
                    before = self.files(project)
                    if contained:
                        with self.assertRaises(InputError):
                            create_draft(project, {'newAtom': values}, current_rows=rows(),
                                         validate_project_spec_model=validate)
                        self.assertEqual(before, self.files(project))
                        continue
                    created = create_draft(project, {'newAtom': values}, current_rows=rows(),
                                           validate_project_spec_model=validate)
                    self.assertEqual('completed', created['outcome'])
                    self.assertEqual([(template, 'C00')], calls)
                    draft = created['savedDraft']
                    target = {'ref_id': draft['ref_id'], 'version': 1}
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        promote_draft(project, {'target': target, 'targetStatus': 'active'}, current_rows=rows(),
                                      validate_project_spec_model=validate)
                    self.assertEqual(before, self.files(project))
                    second = create_draft(project, {'newAtom': {**values, 'body': '\n## Summary\n\nSecond\n'}},
                                          current_rows=rows(), validate_project_spec_model=validate)
                    second_target = {'ref_id': second['savedDraft']['ref_id'], 'version': 1}
                    ready = promote_draft(project, {'target': second_target, 'targetStatus': 'ready'},
                                          current_rows=rows(), validate_project_spec_model=validate)
                    self.assertEqual('ready', ready['artifact']['status'])
                    current = {'ref_id': ready['artifact']['ref_id'], 'version': 1}
                    for status in ('active', 'archived'):
                        moved = change_spec_status(project, {'target': current, 'targetStatus': status}, current_rows=rows(),
                                                   validate_project_spec_model=validate)
                        self.assertEqual(status, moved['artifact']['status'])
                    result = archive_spec_draft(project, {'target': target}, current_rows=rows())
                    self.assertEqual('completed', result['outcome'], result)
                    self.assertEqual('archived', result['artifact']['status'])
                    before = self.files(project)
                    with self.assertRaises((InputError, SourceChanged)):
                        archive_spec_draft(project, {'target': target}, current_rows=rows())
                    self.assertEqual(before, self.files(project))

    def test_asset_body_update_current_and_draft(self):
        for template in ('analysis_report', 'work_report', 'work_log', 'spec_proposal'):
            for situation in ('current', 'draft'):
                for contained in (False, True):
                    with self.subTest(route='direct_update', family='TKT', template=template,
                                      situation=situation, contained=contained):
                        project = self.project()
                        container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                        header = canonical_native_header({'identity': {'atom_id': 'AN-T-2'},
                            'context': {'container': container, 'template': template},
                            'state': {'status': 'draft' if situation == 'draft' else 'in_queue',
                                      'version': 1, 'updated_at': '2026-01-01'}})
                        owner = project.control_root / '001_TICKETS/TASKS/AN-T-1-TASK--owner'
                        path = native_carrier_path(header, 'Example', project_root=project.control_root,
                            owner_directory=owner if contained else project.control_root,
                            owner_template='task' if contained else None)
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) +
                                        '---\n\n## Summary\n\nExample\n\n## Details\n\nOld\n')
                        ref = 'AN-T-2@1-draft' if situation == 'draft' else 'AN-T-2'
                        body = '\n## Summary\n\nExample\n\n## Details\n\nNew\n'
                        before = self.files(project)
                        with self.assertRaises(InputError):
                            direct_update(project, {'target': {'ref_id': ref, 'version': 1},
                                'changes': {'body': body.replace('Example', 'Changed')}},
                                current_rows=capture_native(project).atoms)
                        self.assertEqual(before, self.files(project))
                        result = direct_update(project, {'target': {'ref_id': ref, 'version': 1},
                                                        'changes': {'body': body}},
                                               current_rows=capture_native(project).atoms)
                        self.assertEqual('completed', result['outcome'], result)
                        self.assertEqual(['modify'], [effect['operation'] for effect in result['effects']])
                        capture = capture_native(project)
                        self.assertFalse(capture.errors, capture.errors)
                        row = next(row for row in capture.atoms if row['_exact_ref'] == (ref if situation == 'draft' else ref + '@1'))
                        self.assertEqual(header, row['header_json'])
                        self.assertEqual(body.encode(), row['_content_bytes'])
                        self.assertEqual(path.relative_to(project.root).as_posix(), row['source_path'])

    def test_asset_create_is_direct_in_queue(self):
        for template in ('analysis_report', 'work_report', 'work_log', 'spec_proposal'):
            for contained in (False, True):
                with self.subTest(template=template, contained=contained):
                    project = self.project()
                    container = {'atom': 'AN-T-1'} if contained else {'component': 'C00'}
                    result = create_asset(project, {'newAtom': {'template': template, 'container': container,
                                          'body': '\n## Summary\n\nExample\n'}},
                                          current_rows=capture_native(project).atoms)
                    self.assertEqual('completed', result['outcome'])
                    self.assertEqual('in_queue', result['artifact']['status'])
                    path = project.root / result['artifact']['path']
                    self.assertTrue(path.is_file())
                    self.assertNotIn('01_draft', path.parts)
                    target = {'ref_id': result['artifact']['ref_id'], 'version': 1}
                    before = self.files(project)
                    with self.assertRaises(InputError):
                        archive_ticket(project, {'target': target}, current_rows=capture_native(project).atoms)
                    self.assertEqual(before, self.files(project))
                    if contained:
                        before = self.files(project)
                        with self.assertRaises(InputError):
                            change_ticket_status(project, {'target': target, 'targetStatus': 'complete'},
                                                 current_rows=capture_native(project).atoms, check_definition=lambda: None)
                        self.assertEqual(before, self.files(project))
                    status = 'done' if contained else 'complete'
                    result = change_ticket_status(project, {'target': target, 'targetStatus': status},
                                                  current_rows=capture_native(project).atoms, check_definition=lambda: None)
                    self.assertEqual('completed', result['outcome'], result)
                    self.assertEqual(status, result['artifact']['status'])
                    if not contained:
                        self.assertIn('08_complete', (project.root / result['artifact']['path']).parts)


class NonTicketRevisionMatrix(unittest.TestCase):
    write = fixtures.NativeDraftTests.write
    spec = fixtures.NativeRevisionCarrierTests.spec

    def test_generic_spec_and_pmeta_revision(self):
        for family in ('SPEC', 'PMETA'):
            with self.subTest(family=family):
                fixtures.NativeRevisionCarrierTests.setUp(self)
                if family == 'SPEC':
                    path = self.spec('UNIT_C9/__DES/__DOM/AN-S-4-DOM--example.md', 'AN-S-4', 'DES/DOM')
                    atom_id, status = 'AN-S-4', 'ready'
                else:
                    path = self.write('_PMETA/AN-P-4-ACTION--example.md', 'AN-P-4', template='action')
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


class ComponentContractMatrix(unittest.TestCase):
    write = fixtures.NativeDraftTests.write
    spec = fixtures.NativeRevisionCarrierTests.spec

    def test_new_and_revision_routes(self):
        fixtures.ComponentContractLifecycleTests.setUp(self)
        rows = lambda: capture_native(self.selection).atoms
        created = create_draft(self.selection, self.new, current_rows=rows(), structure_snapshot=self.snapshot)
        self.assertEqual('completed', created['outcome'])
        draft = created['savedDraft']
        before = {p: p.read_bytes() for p in self.control.rglob('*.md')}
        with self.assertRaises(InputError):
            promote_draft(self.selection, {'target': {'ref_id': draft['ref_id'], 'version': 1},
                          'targetStatus': 'active'}, current_rows=rows(), structure_snapshot=self.snapshot)
        self.assertEqual(before, {p: p.read_bytes() for p in self.control.rglob('*.md')})
        published = promote_draft(self.selection, {'target': {'ref_id': draft['ref_id'], 'version': 1},
                                  'targetStatus': 'ready'}, current_rows=rows(), structure_snapshot=self.snapshot)
        self.assertEqual('ready', published['artifact']['status'])
        revision = create_draft(self.selection,
            {'sourceCurrent': {'ref_id': published['artifact']['ref_id'], 'version': 1}},
            current_rows=rows(), structure_snapshot=self.snapshot)
        self.assertEqual('completed', revision['outcome'])
        result = promote_draft(self.selection,
            {'target': {'ref_id': revision['savedDraft']['ref_id'], 'version': 2}, 'targetStatus': 'ready'},
            current_rows=rows(), structure_snapshot=self.snapshot)
        self.assertEqual('completed', result['outcome'], result)
        self.assertIn(published['artifact']['ref_id'] + '@1', [row['_exact_ref'] for row in rows()])


if __name__ == '__main__':
    unittest.main()
