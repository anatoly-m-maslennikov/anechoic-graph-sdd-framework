"""Generated native lifecycle paths; each case uses a fresh project."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import time
import unittest

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native, parse_structure
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import NativeProjectSelection
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import LIFECYCLE_TOOLS, execute_native_lifecycle


LIFECYCLE_TEMPLATES = {
    'TKT': ('task', 'epic', 'problem', 'question', 'code_spec_mismatch', 'opportunity',
            'analysis_report', 'work_report', 'work_log', 'spec_proposal'),
    'SPEC': (None, 'DECISION', 'PKG', 'POLICY', 'action', 'component_contract', 'project_contract', 'component_manifest',
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


def lifecycle_transition_cases():
    cases = []
    for template in ('task', 'epic'):
        cases.extend({'route': 'change_status', 'family': 'TKT', 'template': template,
                      'situation': 'current', 'contained': False,
                      'source_status': source, 'target_status': target}
                     for source, target in (('backlog', 'in_queue'), ('in_queue', 'done'),
                                            ('in_queue', 'canceled')))
    for template in ('problem', 'question', 'code_spec_mismatch', 'opportunity'):
        cases.extend({'route': 'change_status', 'family': 'TKT', 'template': template,
                      'situation': 'current', 'contained': False,
                      'source_status': source, 'target_status': target}
                     for source, target in (('in_queue', 'resolved'), ('in_queue', 'canceled')))
    for template in ('analysis_report', 'work_report', 'work_log', 'spec_proposal'):
        cases.append({'route': 'change_status', 'family': 'TKT', 'template': template,
                      'situation': 'current', 'contained': False,
                      'source_status': 'in_queue', 'target_status': 'complete'})
    return cases


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle_route_support import LifecycleRouteSupport


class LifecycleRouteMatrix(LifecycleRouteSupport, unittest.TestCase):
    def test_generated_route_grid(self):
        from unittest.mock import patch

        body = '\n## Summary\n\nExample\n\n## Guarantee\n\nThe graph includes imports.\n'
        changed = body + '\nMore detail.\n'
        assets = {'analysis_report', 'work_report', 'work_log', 'spec_proposal'}
        project_specs = {'axiom', 'applicable_principle', 'project_contract'}
        cases = list(lifecycle_cases())
        self.assertEqual(1624, len(cases))
        cases.extend(lifecycle_transition_cases())
        self.assertEqual(1642, len(cases))
        self.assertEqual(set(LIFECYCLE_ROUTES), {name.removeprefix('atom_lifecycle_') for name in LIFECYCLE_TOOLS})
        with patch('FEATURE_PROGRAMMATIC.FEATURE_TOOLS.native_workflow_definition.bind_status_specifications', return_value=lambda: None):
            for case in cases:
                source_status = case.get('source_status', ({'new': 'none', 'current': 'in_queue', 'draft': 'draft', 'archived': 'archived'}[case['situation']]
                    if case['family'] == 'TKT' else
                    {'new': 'none', 'current': 'active' if case['route'] == 'archive' else 'ready', 'draft': 'draft', 'archived': 'archived'}[case['situation']]
                    if case['family'] == 'SPEC' else
                    {'new': 'none', 'current': 'active', 'draft': 'draft', 'archived': 'archived'}[case['situation']]))
                target_status = case.get('target_status', {'create_draft': 'draft', 'update': 'draft', 'create_asset': 'in_queue',
                    'direct_update': source_status, 'promote_draft': {'TKT': 'backlog', 'SPEC': 'ready', 'PROJECT_CONFIG': 'active'}[case['family']],
                    'change_status': 'active' if case['family'] == 'SPEC' else ('resolved' if case['template'] in {'problem', 'question', 'code_spec_mismatch', 'opportunity'} else 'done'),
                    'archive': 'archived'}[case['route']])
                expected = self._grid_expected(case, assets, project_specs)
                started = time.monotonic()
                outcome = 'FAIL'
                actual = 'not_observed'
                result = self._outcome.result
                prior_failures = len(result.failures) + len(result.errors)
                try:
                    with self.subTest(**case), tempfile.TemporaryDirectory() as directory:
                        actual = self._run_grid_case(case, directory, body, changed, assets, project_specs)
                    outcome = 'PASS' if prior_failures == len(result.failures) + len(result.errors) else 'FAIL'
                finally:
                    elapsed = time.monotonic() - started
                    report = {**case, 'source_status': source_status, 'target_status': target_status,
                        'expected': 'accepted' if expected else 'rejected',
                        'actual': actual, 'result': outcome,
                        'elapsed_seconds': round(elapsed, 6),
                        'coverage': 'transition' if expected else 'negative_case'}
                    print(json.dumps(report, sort_keys=True))

    def _grid_project(self, directory, body):
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
        project = NativeProjectSelection(
            root=root, control_root=control, control_relative=control.relative_to(root),
            instance_id='a' * 64, project_name='Test', project_prefix='AN',
            manifest_path=manifest, manifest_ref='AN-S-1@1',
            manifest_sha256=sha256(manifest.read_bytes()).hexdigest(),
        )
        component = control / 'UNIT_C9'; component.mkdir()
        declaration = control / 'AN-S-2-SPEC--component.md'
        declaration.write_text('---\n' + yaml.safe_dump({'identity': {'atom_id': 'AN-S-2'},
            'context': {'container': {'component': 'C00'}, 'lens': 'SPEC'},
            'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'}}) + '---\n' + body)
        snapshot = parse_structure(json.dumps({'model_sha256': 'model', 'project': {'ref': 'AN-S-1@1', 'sha256': sha256(manifest.read_bytes()).hexdigest()},
            'components': {'C9': {'parent': 'C00', 'ref': 'AN-S-2@1', 'sha256': sha256(declaration.read_bytes()).hexdigest(),
                'fields': {'name': 'Unit', 'lens_whitelist': None}, 'source_path': declaration.relative_to(control).as_posix()}}, 'packages': {}}).encode())
        owner_header = canonical_native_header({'identity': {'atom_id': 'AN-T-1'},
            'context': {'container': {'component': 'C00'}, 'template': 'task'},
            'state': {'status': 'in_queue', 'version': 1, 'updated_at': '2026-01-01'}})
        owner_path = native_carrier_path(owner_header, 'Owner', project_root=control, owner_directory=control)
        owner_path.parent.mkdir(parents=True, exist_ok=True); owner_path.write_text(
            '---\n' + yaml.safe_dump(owner_header, sort_keys=False) + '---\n\n## Summary\n\nOwner\n')
        owner_dir = owner_path.with_suffix(''); return project, component, snapshot, owner_dir

    def _grid_carrier(self, case, project, component, owner_dir, container, body):
        family, template, situation, contained, route = (case[k] for k in ('family', 'template', 'situation', 'contained', 'route'))
        control = project.control_root
        atom_id = {'TKT': 'AN-T-2', 'SPEC': 'AN-S-3', 'PROJECT_CONFIG': 'AN-C-1'}[family]
        if family == 'SPEC' and template == 'project_manifest' and situation == 'current' and not contained:
            atom_id = 'AN-S-1'
        elif situation != 'new':
            context = {'container': container}
            if template is not None:
                context['template'] = template
            if family == 'SPEC':
                tiers = {'project_manifest': -1, 'axiom': 0, 'component_contract': 0,
                         'project_contract': 0, 'applicable_principle': 2}
                context.update(lens='SPEC', tier=tiers.get(template, 1))
            status = {'current': ('active' if route == 'archive' else 'ready') if family == 'SPEC' else 'active' if family == 'PROJECT_CONFIG' else 'in_queue',
                      'draft': 'draft', 'archived': 'archived'}[situation]
            status = case.get('source_status', status)
            if family == 'PROJECT_CONFIG' and template is None and situation != 'draft':
                pass
            else:
                version = 2 if family == 'PROJECT_CONFIG' and situation == 'draft' and template is not None and not contained else 1
                if version == 2:
                    previous = canonical_native_header({'identity': {'atom_id': atom_id}, 'context': context,
                        'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'}})
                    previous_path = native_carrier_path(previous, 'Example', project_root=control, owner_directory=control)
                    previous_path.parent.mkdir(parents=True, exist_ok=True); previous_path.write_text(
                        '---\n' + yaml.safe_dump(previous, sort_keys=False) + '---\n' + body)
                header = canonical_native_header({'identity': {'atom_id': atom_id}, 'context': context,
                    'state': {'status': status, 'version': version, 'updated_at': '2026-01-01'}})
                path = native_carrier_path(header, 'Example', project_root=control,
                    owner_directory=owner_dir if contained else component if family == 'SPEC' and container == {'component': 'C9'} else control,
                    owner_template='task' if contained else None)
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(
                    '---\n' + yaml.safe_dump(header, sort_keys=False) + '---\n' + body)
        return atom_id

    def _grid_arguments(self, case, atom_id, container, body, changed):
        family, template, situation, contained, route = (case[k] for k in
            ('family', 'template', 'situation', 'contained', 'route'))
        version = 2 if family == 'PROJECT_CONFIG' and situation == 'draft' and template is not None and not contained else 1
        ref = atom_id + ({'draft': f'@{version}-draft', 'archived': '@1'}.get(situation, ''))
        target = {'ref_id': ref, 'version': version}
        values = {'template': template, 'container': container, 'body': body}
        if family == 'SPEC':
            values['lens'] = 'SPEC'
        status = None
        if route in {'create_draft', 'update'}:
            args = {'newAtom': values} if situation == 'new' else {'sourceCurrent': target, 'changes': {'body': changed}}
        elif route == 'create_asset':
            args = {'newAtom': values} if situation == 'new' else {'target': target}
        elif route == 'direct_update':
            args = {'target': target, 'changes': {'body': changed}}
        elif route == 'promote_draft':
            args = {'target': target, 'targetStatus': {'TKT': 'backlog', 'SPEC': 'ready', 'PROJECT_CONFIG': 'active'}[family]}
        elif route == 'change_status':
            status = case.get('target_status', 'active' if family == 'SPEC' else ('resolved' if template in {'problem', 'question', 'code_spec_mismatch', 'opportunity'} else 'done'))
            args = {'target': target, 'targetStatus': status}
        else:
            args = {'target': target}
        return args, status

    def _grid_expected(self, case, assets, project_specs):
        family, template, situation, contained, route = (case[k] for k in
            ('family', 'template', 'situation', 'contained', 'route'))
        return (
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
                (family == 'TKT' and self._grid_ticket_transition_supported(case) or
                 family == 'SPEC' and not contained and template != 'project_manifest') or
            route == 'archive' and family == 'SPEC' and not contained and
                (situation == 'draft' or situation == 'current' and template != 'project_manifest')
        )

    def _grid_ticket_transition_supported(self, case):
        template = case['template']
        source = case.get('source_status', 'in_queue')
        target = case.get('target_status', 'resolved' if template in {'problem', 'question', 'code_spec_mismatch', 'opportunity'} else 'done')
        if template in {'task', 'epic'}:
            return (source == 'backlog' and target == 'in_queue' or
                    source in {'in_queue', 'active'} and target in {'done', 'canceled'} or
                    source == 'active' and target == 'in_queue')
        if template in {'problem', 'question', 'code_spec_mismatch', 'opportunity'}:
            return (source == 'backlog' and target == 'in_queue' or
                    source in {'in_queue', 'active'} and target in {'resolved', 'canceled'} or
                    source == 'active' and target == 'in_queue')
        return (template in {'analysis_report', 'work_report', 'work_log', 'spec_proposal'}
                and (target == 'done' or not case['contained'] and source == 'in_queue' and target == 'complete'))

    def _run_grid_case(self, case, directory, body, changed, assets, project_specs):
        family, template, contained, route = (case[k] for k in ('family', 'template', 'contained', 'route'))
        project, component, snapshot, owner_dir = self._grid_project(directory, body)
        container = {'atom': 'AN-T-1'} if contained else {'component': 'C00' if template in project_specs or template == 'project_manifest' or family != 'SPEC' else 'C9'}
        atom_id = self._grid_carrier(case, project, component, owner_dir, container, body)
        capture = capture_native(project)
        self.assertFalse(capture.errors, capture.errors)
        before = self.files(project)
        args, status = self._grid_arguments(case, atom_id, container, body, changed)
        expected = self._grid_expected(case, assets, project_specs)
        result = execute_native_lifecycle(
            project, 'atom_lifecycle_' + route, args, capture, None,
            previous_capture=None, ticket_labels=(), validate_project_spec=lambda *args: None,
            admitted_structure=snapshot,
        )
        if result['outcome'] != 'completed':
            self.assertFalse(expected, result)
            self.assertFalse(result['effects'], result)
            if result['outcome'] == 'needs_input':
                self.assertTrue(result['requested_input'], result)
            else:
                self.assertEqual('failed', result['outcome'], result)
                self.assertEqual(['source_changed'], [item['code'] for item in result['errors']])
            self.assertEqual(before, self.files(project))
            return 'rejected'
        self._check_grid_result(case, result, project, component, owner_dir, container, body, changed,
                                before, atom_id, status, project_specs, expected)
        return 'accepted'

    def _check_grid_result(self, case, result, project, component, owner_dir, container, body, changed,
                           before, atom_id, status, project_specs, expected):
        family, template, situation, contained, route = (case[k] for k in
            ('family', 'template', 'situation', 'contained', 'route'))
        root, control = project.root, project.control_root
        self.assertTrue(expected, result); self.assertEqual('completed', result['outcome'], result)
        self.assertTrue(result['effects'], result); saved = result.get('savedDraft') or result['artifact']
        saved_path = root / saved['path']
        self.assertTrue(saved_path.is_file())
        expected_version = 2 if (situation == 'current' and route in {'create_draft', 'update'} or family == 'PROJECT_CONFIG' and situation == 'draft' and template is not None and not contained) else 1
        self.assertEqual(atom_id, saved['atom_id']); self.assertEqual(expected_version, saved['version'])
        expected_status = ('draft' if route in {'create_draft', 'update'} else
            'in_queue' if route == 'create_asset' else
            {'TKT': 'backlog', 'SPEC': 'ready', 'PROJECT_CONFIG': 'active'}[family] if route == 'promote_draft' else
            status if route == 'change_status' else 'archived' if route == 'archive' else
            'draft' if situation == 'draft' else 'in_queue')
        self.assertEqual(expected_status, saved['status'].lower()); expected_ref = (
            f"{saved['atom_id']}@{expected_version}-draft" if expected_status == 'draft' else
                        f"{saved['atom_id']}@{expected_version}" if expected_status == 'archived' else saved['atom_id'])
        self.assertEqual(expected_ref, saved['ref_id']); operations = [
            effect['operation'] for effect in result['effects'] if effect.get('evidence') != 'directory']
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
            self.assertEqual(0 if template in {'axiom', 'project_contract'} else 2, row['header_json']['tier'])
        self.assertEqual((changed if route in {'direct_update', 'update', 'create_draft'} and situation != 'new' else body).encode(), row['_content_bytes'])
        self.assertNotEqual(before, self.files(project))
