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


LIFECYCLE_TEMPLATES = {
    'TKT': ('task', 'epic', 'problem', 'question', 'code_spec_mismatch', 'opportunity',
            'analysis_report', 'work_report', 'work_log', 'spec_proposal'),
    'SPEC': (None, 'DECISION', 'PKG', 'POLICY', 'action', 'component_contract', 'component_manifest',
             'project_goal', 'project_manifest', 'contract', 'step', 'workflow', 'axiom', 'applicable_principle'),
    'PROJECT_CONFIG': ('action', 'step', 'workflow', None),
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
        return {p.relative_to(project.root): p.read_bytes() for p in project.control_root.rglob('*') if p.is_file()}

    def test_generated_route_grid(self):
        from unittest.mock import patch
        sys.path.insert(0, str(ENGINE / 'MCP_PATCHBAY_C21' / 'FEATURE_MCP'))
        from native_query import NativeQueryOwner

        body = '\n## Summary\n\nExample\n\n## Guarantee\n\nThe graph includes imports.\n'
        changed = body + '\nMore detail.\n'
        assets = {'analysis_report', 'work_report', 'work_log', 'spec_proposal'}
        project_specs = {'axiom', 'applicable_principle'}
        cases = list(lifecycle_cases())
        self.assertEqual(1568, len(cases))
        with patch('native_workflow_definition.bind_status_specifications', return_value=lambda: None):
            for case in cases:
                with self.subTest(**case), tempfile.TemporaryDirectory() as directory:
                    family, template, situation, contained, route = (case[k] for k in
                        ('family', 'template', 'situation', 'contained', 'route'))
                    root = Path(directory).resolve()
                    (root / '.git').mkdir()
                    control = root / '.anechoic_test'
                    control.mkdir()
                    manifest = control / 'AN-S-1-PROJECT_MANIFEST--manifest.md'
                    manifest.write_text("""---
identity: {atom_id: AN-S-1}
context: {container: {component: C00}, tier: -1, lens: SPEC, template: project_manifest}
state: {status: active, version: 1, updated_at: '2026-01-01'}
---
## Summary

Manifest

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ProjectManifest
declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name='Test', prefix='AN', lens_whitelist=['DES', 'SPEC']))
```
""")
                    project = SimpleNamespace(root=root, control_root=control, manifest_path=manifest,
                        manifest_sha256=sha256(manifest.read_bytes()).hexdigest(), project_prefix='AN')
                    component = control / 'UNIT_C9'
                    component.mkdir()
                    declaration = control / 'AN-S-2-SPEC--component.md'
                    declaration.write_text('---\n' + yaml.safe_dump({'identity': {'atom_id': 'AN-S-2'},
                        'context': {'container': {'component': 'C00'}, 'lens': 'SPEC'},
                        'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'}}) + '---\n' + body)
                    record = SimpleNamespace(source_path=declaration.relative_to(control).as_posix(),
                        sha256=sha256(declaration.read_bytes()).hexdigest(), parent='C00', lens_whitelist=None)
                    snapshot = SimpleNamespace(components={'C9': record}, component=lambda key: {'C9': record}[key])
                    owner_header = canonical_native_header({'identity': {'atom_id': 'AN-T-1'},
                        'context': {'container': {'component': 'C00'}, 'template': 'task'},
                        'state': {'status': 'in_queue', 'version': 1, 'updated_at': '2026-01-01'}})
                    owner_path = native_carrier_path(owner_header, 'Owner', project_root=control, owner_directory=control)
                    owner_path.parent.mkdir(parents=True, exist_ok=True)
                    owner_path.write_text('---\n' + yaml.safe_dump(owner_header, sort_keys=False) + '---\n\n## Summary\n\nOwner\n')
                    owner_dir = owner_path.with_suffix('')
                    container = {'atom': 'AN-T-1'} if contained else {'component': 'C00' if template in project_specs or template == 'project_manifest' or family != 'SPEC' else 'C9'}
                    atom_id = {'TKT': 'AN-T-2', 'SPEC': 'AN-S-3', 'PROJECT_CONFIG': 'AN-P-1'}[family]
                    if family == 'SPEC' and template == 'project_manifest' and situation == 'current' and not contained:
                        atom_id = 'AN-S-1'
                    elif situation != 'new':
                        context = {'container': container}
                        if template is not None:
                            context['template'] = template
                        if family == 'SPEC':
                            context.update(lens='SPEC', tier=-1 if template in {'axiom', 'project_manifest'} else 2 if template == 'applicable_principle' else 1)
                        status = {'current': ('active' if route == 'archive' else 'ready') if family == 'SPEC' else 'active' if family == 'PROJECT_CONFIG' else 'in_queue',
                                  'draft': 'draft', 'archived': 'archived'}[situation]
                        if family == 'PROJECT_CONFIG' and template is None and situation != 'draft':
                            pass
                        else:
                            version = 2 if family == 'PROJECT_CONFIG' and situation == 'draft' and template is not None and not contained else 1
                            if version == 2:
                                previous = canonical_native_header({'identity': {'atom_id': atom_id}, 'context': context,
                                    'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'}})
                                previous_path = native_carrier_path(previous, 'Example', project_root=control, owner_directory=control)
                                previous_path.parent.mkdir(parents=True, exist_ok=True)
                                previous_path.write_text('---\n' + yaml.safe_dump(previous, sort_keys=False) + '---\n' + body)
                            header = canonical_native_header({'identity': {'atom_id': atom_id}, 'context': context,
                                'state': {'status': status, 'version': version, 'updated_at': '2026-01-01'}})
                            path = native_carrier_path(header, 'Example', project_root=control,
                                owner_directory=owner_dir if contained else component if family == 'SPEC' and container == {'component': 'C9'} else control,
                                owner_template='task' if contained else None)
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text('---\n' + yaml.safe_dump(header, sort_keys=False) + '---\n' + body)
                    capture = capture_native(project)
                    self.assertFalse(capture.errors, capture.errors)
                    before = self.files(project)
                    version = 2 if family == 'PROJECT_CONFIG' and situation == 'draft' and template is not None and not contained else 1
                    ref = atom_id + ({'draft': f'@{version}-draft', 'archived': '@1'}.get(situation, ''))
                    target = {'ref_id': ref, 'version': version}
                    values = {'template': template, 'container': container, 'body': body}
                    if family == 'SPEC':
                        values['lens'] = 'SPEC'
                    if route in {'create_draft', 'update'}:
                        args = {'newAtom': values} if situation == 'new' else {'sourceCurrent': target, 'changes': {'body': changed}}
                    elif route == 'create_asset':
                        args = {'newAtom': values} if situation == 'new' else {'target': target}
                    elif route == 'direct_update':
                        args = {'target': target, 'changes': {'body': changed}}
                    elif route == 'promote_draft':
                        args = {'target': target, 'targetStatus': {'TKT': 'backlog', 'SPEC': 'ready', 'PROJECT_CONFIG': 'active'}[family]}
                    elif route == 'change_status':
                        status = 'active' if family == 'SPEC' else ('resolved' if template in {'problem', 'question', 'code_spec_mismatch', 'opportunity'} else 'done')
                        args = {'target': target, 'targetStatus': status}
                    else:
                        args = {'target': target}
                    owner = object.__new__(NativeQueryOwner)
                    owner.selection = project
                    owner._projection_selection = None
                    owner._capture = capture
                    owner._inputs = SimpleNamespace(ticket_labels=(), validate_project_spec=lambda *args: None)
                    expected = (
                        route == 'create_draft' and situation == 'new' and
                            ((family == 'TKT' and template in {'task', 'epic'}) or
                             (family == 'SPEC' and not contained and template in project_specs | {'component_contract'})) or
                        route in {'create_draft', 'update'} and situation == 'current' and
                            ((family == 'TKT' and template in {'task', 'epic'}) or
                             (family == 'PROJECT_CONFIG' and template is not None and not contained) or
                             (family == 'SPEC' and template != 'project_manifest' and not contained)) or
                        route == 'create_asset' and situation == 'new' and family == 'TKT' and template in assets or
                        route == 'direct_update' and situation in {'current', 'draft'} and family == 'TKT' and template in assets or
                        route == 'promote_draft' and situation == 'draft' and
                            ((family == 'TKT' and template in {'task', 'epic'}) or
                             (family == 'SPEC' and not contained and template in {None, 'component_contract'} | project_specs) or
                             (family == 'PROJECT_CONFIG' and template is not None and not contained)) or
                        route == 'change_status' and situation == 'current' and
                            (family == 'TKT' or family == 'SPEC' and not contained and template != 'project_manifest') or
                        route == 'archive' and family == 'SPEC' and not contained and
                            (situation == 'draft' or situation == 'current' and template != 'project_manifest')
                    )
                    try:
                        result = owner._dispatch_lifecycle('atom_lifecycle_' + route, args, capture.atoms, snapshot)
                    except (InputError, SourceChanged) as error:
                        self.assertFalse(expected, str(error))
                        self.assertEqual(before, self.files(project))
                        continue
                    self.assertTrue(expected, result)
                    self.assertEqual('completed', result['outcome'], result)
                    self.assertTrue(result['effects'], result)
                    saved = result.get('savedDraft') or result['artifact']
                    saved_path = root / saved['path']
                    self.assertTrue(saved_path.is_file())
                    expected_version = 2 if (situation == 'current' and route in {'create_draft', 'update'} or family == 'PROJECT_CONFIG' and situation == 'draft' and template is not None and not contained) else 1
                    self.assertEqual(atom_id, saved['atom_id'])
                    self.assertEqual(expected_version, saved['version'])
                    expected_status = ('draft' if route in {'create_draft', 'update'} else
                        'in_queue' if route == 'create_asset' else
                        {'TKT': 'backlog', 'SPEC': 'ready', 'PROJECT_CONFIG': 'active'}[family] if route == 'promote_draft' else
                        status if route == 'change_status' else 'archived' if route == 'archive' else
                        'draft' if situation == 'draft' else 'in_queue')
                    self.assertEqual(expected_status, saved['status'].lower())
                    expected_ref = (f"{saved['atom_id']}@{expected_version}-draft" if expected_status == 'draft' else
                                    f"{saved['atom_id']}@{expected_version}" if expected_status == 'archived' else saved['atom_id'])
                    self.assertEqual(expected_ref, saved['ref_id'])
                    operations = [effect['operation'] for effect in result['effects'] if effect.get('evidence') != 'directory']
                    expected_operations = (['create'] if route in {'create_draft', 'update', 'create_asset'} else
                        ['modify'] if route == 'direct_update' else
                        ['create', 'modify', 'remove'] if family == 'PROJECT_CONFIG' and route == 'promote_draft' else
                        ['create', 'remove'])
                    self.assertEqual(expected_operations, operations)
                    self.assertTrue(any(effect['target'] == saved['path'] for effect in result['effects']))
                    after = capture_native(project)
                    self.assertFalse(after.errors, after.errors)
                    exact_ref = expected_ref if '@' in expected_ref else f'{expected_ref}@{expected_version}'
                    row = next(row for row in after.atoms if row['_exact_ref'] == exact_ref)
                    self.assertEqual(saved['path'], row['source_path'])
                    derived = native_carrier_path(row['header_json'], 'Example', project_root=control,
                        owner_directory=owner_dir if contained else component if family == 'SPEC' and container == {'component': 'C9'} else control,
                        owner_template='task' if contained else None)
                    self.assertEqual(derived, saved_path)
                    self.assertEqual(expected_status, row['status'])
                    if family == 'SPEC' and template in project_specs:
                        self.assertEqual(-1 if template == 'axiom' else 2, row['header_json']['tier'])
                    self.assertEqual((changed if route in {'direct_update', 'update', 'create_draft'} and situation != 'new' else body).encode(), row['_content_bytes'])
                    self.assertNotEqual(before, self.files(project))

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
                    carrier_root = project.control_root
                    if template == 'axiom':
                        for invalid in ({'tier': 0}, {'lens': 'DES'}, {'container': {'component': 'C9'}}):
                            with self.subTest(invalid=invalid), self.assertRaises(InputError):
                                create_draft(project, {'newAtom': {**values, **invalid}}, current_rows=rows(),
                                             validate_project_spec_model=validate)
                        self.assertEqual(before, self.files(project))
                    created = create_draft(project, {'newAtom': values}, current_rows=rows(),
                                           validate_project_spec_model=validate)
                    self.assertEqual('completed', created['outcome'])
                    self.assertEqual([(template, 'C00')], calls)
                    draft = created['savedDraft']
                    self.assertEqual(carrier_root / '01_draft', (project.root / draft['path']).parent)
                    if template == 'axiom':
                        self.assertTrue(draft['ref_id'].startswith('AN-S-'))
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
                    self.assertEqual(carrier_root / '02_ready', (project.root / ready['artifact']['path']).parent)
                    current = {'ref_id': ready['artifact']['ref_id'], 'version': 1}
                    for status, directory in (('active', ''), ('archived', '09_archived')):
                        moved = change_spec_status(project, {'target': current, 'targetStatus': status}, current_rows=rows(),
                                                   validate_project_spec_model=validate)
                        self.assertEqual(status, moved['artifact']['status'])
                        self.assertEqual(carrier_root / directory, (project.root / moved['artifact']['path']).parent)
                    result = archive_spec_draft(project, {'target': target}, current_rows=rows())
                    self.assertEqual('completed', result['outcome'], result)
                    self.assertEqual('archived', result['artifact']['status'])
                    self.assertEqual(carrier_root / '09_archived', (project.root / result['artifact']['path']).parent)
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
