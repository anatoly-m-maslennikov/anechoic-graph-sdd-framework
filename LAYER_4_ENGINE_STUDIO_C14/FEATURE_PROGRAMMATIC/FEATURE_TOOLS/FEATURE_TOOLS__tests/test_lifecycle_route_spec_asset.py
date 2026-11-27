"""Generated native lifecycle paths; each case uses a fresh project."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import sys
import unittest

import yaml

TOOLS = Path(__file__).resolve().parents[1]
ENGINE = TOOLS.parents[1]
sys.path[:0] = [str(TOOLS), str(ENGINE / 'IWE_CONSOLE_C43')]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import capture_native
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import InputError, SourceChanged
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_asset
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import canonical_native_header
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_path
import FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.test_native_lifecycle_draft as fixtures
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import create_draft, promote_draft
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (archive_spec_draft, archive_ticket, change_spec_status,
                                           change_ticket_status, direct_update)






from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle_route_support import LifecycleRouteSupport


class Model:
    enabled = True

    def project_spec_template(self, template):
        return ('Probe', 0, self.enabled) if template == 'probe' else None

    def validate_project_spec(self, template, header, owner, body):
        context = header.get('context', {})
        if (template != 'probe' or owner != 'C00' or header.get('tier') != 0
                or context.get('lens') != 'SPEC' or '## Guarantee' not in body):
            raise ValueError('Invalid Project SPEC')


class LifecycleRouteMatrix(LifecycleRouteSupport, unittest.TestCase):
    def test_project_template_creation_and_disabled_history(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(project.manifest_path.read_text().replace('component: C0}', 'component: C00}'))
        project = replace(project, manifest_sha256=sha256(project.manifest_path.read_bytes()).hexdigest())
        values = {'template': 'probe', 'container': {'component': 'C00'}, 'lens': 'SPEC',
                  'body': '\n## Summary\n\nProbe\n\n## Guarantee\n\nThe Project records the decision.\n'}

        model = Model()
        validate = model.validate_project_spec
        created = create_draft(project, {'newAtom': values}, current_rows=capture_native(project).atoms,
                               validate_project_spec_model=validate)
        self.assertEqual('completed', created['outcome'], created)
        for invalid in ({'tier': 2}, {'lens': 'DES'}, {'template': 'unknown'},
                        {'body': '\n## Summary\n\nMissing Guarantee\n'}):
            with self.subTest(invalid=invalid), self.assertRaises(InputError):
                create_draft(project, {'newAtom': {**values, **invalid}},
                             current_rows=capture_native(project).atoms, validate_project_spec_model=validate)
        model.enabled = False
        before = self.files(project)
        with self.assertRaises(InputError):
            create_draft(project, {'newAtom': values}, current_rows=capture_native(project).atoms,
                         validate_project_spec_model=validate)
        self.assertEqual(before, self.files(project))
        target = {'ref_id': created['savedDraft']['ref_id'], 'version': 1}
        self.assertTrue(any(row['_exact_ref'] == target['ref_id'] for row in capture_native(project).atoms))
        ready = promote_draft(project, {'target': target, 'targetStatus': 'ready'},
                              current_rows=capture_native(project).atoms, validate_project_spec_model=validate)
        self.assertEqual('ready', ready['artifact']['status'], ready)
        current = {'ref_id': ready['artifact']['ref_id'], 'version': 1}
        revision = create_draft(project, {'sourceCurrent': current}, current_rows=capture_native(project).atoms)
        self.assertEqual('completed', revision['outcome'], revision)
        promoted = promote_draft(project, {'target': {'ref_id': revision['savedDraft']['ref_id'], 'version': 2},
                                  'targetStatus': 'ready'}, current_rows=capture_native(project).atoms,
                                  validate_project_spec_model=validate)
        self.assertEqual('ready', promoted['artifact']['status'], promoted)
        self.assertTrue(any(row['id'] == current['ref_id'] and row['version'] == 1
                            and row['status_group'] == 'Archived' for row in capture_native(project).atoms))

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
                    self._check_project_spec_template(template, contained)

    def test_project_spec_checks_candidate_status_before_writing(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(project.manifest_path.read_text().replace('component: C0}', 'component: C00}'))
        project = replace(project, manifest_sha256=sha256(project.manifest_path.read_bytes()).hexdigest())
        values = {'template': 'axiom', 'container': {'component': 'C00'}, 'lens': 'SPEC',
                  'body': '\n## Summary\n\nExample\n'}

        def allow(template, header, owner, body):
            return None

        def reject(template, header, owner, body):
            if header['state']['status'] != 'draft':
                raise ValueError('Status is not enabled')

        def publish(draft, validate):
            target = {'ref_id': draft['ref_id'], 'version': draft['version']}
            return promote_draft(project, {'target': target, 'targetStatus': 'ready'},
                                 current_rows=capture_native(project).atoms, validate_project_spec_model=validate)

        first = create_draft(project, {'newAtom': values}, current_rows=capture_native(project).atoms,
                             validate_project_spec_model=allow)['savedDraft']
        before = self.files(project)
        with self.assertRaisesRegex(InputError, 'Status is not enabled'):
            publish(first, reject)
        self.assertEqual(before, self.files(project))

        ready = publish(first, allow)['artifact']
        target = {'ref_id': ready['ref_id'], 'version': ready['version']}
        revision = create_draft(project, {'sourceCurrent': target}, current_rows=capture_native(project).atoms)
        before = self.files(project)
        with self.assertRaisesRegex(InputError, 'Status is not enabled'):
            publish(revision['savedDraft'], reject)
        with self.assertRaisesRegex(InputError, 'Status is not enabled'):
            change_spec_status(project, {'target': target, 'targetStatus': 'active'},
                               current_rows=capture_native(project).atoms, validate_project_spec_model=reject)
        self.assertEqual(before, self.files(project))

    def test_archive_rejects_manifest_property_with_a_plain_des_filename(self):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        owner = project.control_root / 'META_ONTOLOGY_C9'
        header = canonical_native_header({
            'identity': {'atom_id': 'AN-S-2'},
            'context': {'container': {'component': 'C9'}, 'tier': 4, 'lens': 'DES', 'template': 'manifest_property'},
            'state': {'status': 'active', 'version': 1, 'updated_at': '2026-01-01'},
        })
        canonical = native_carrier_path(header, 'Example', project_root=project.control_root,
                                        owner_directory=owner)
        path = canonical.with_name('AN-S-2-DES--example.md')
        path.parent.mkdir(parents=True)
        path.write_text('---\n' + yaml.safe_dump(header) + '---\n\n## Summary\n\nExample\n')
        before = self.files(project)
        capture = capture_native(project)
        with self.assertRaisesRegex(InputError, 'path disagrees'):
            change_spec_status(project, {'target': {'ref_id': 'AN-S-2', 'version': 1}, 'targetStatus': 'archived'},
                               current_rows=capture.atoms, previous_capture=capture)
        self.assertEqual(before, self.files(project))

    def _check_project_spec_template(self, template, contained):
        fixtures.NativeRevisionCarrierTests.setUp(self)
        project = self.selection
        project.manifest_path.write_text(project.manifest_path.read_text().replace('component: C0}', 'component: C00}'))
        self.selection = project = replace(
            project, manifest_sha256=sha256(project.manifest_path.read_bytes()).hexdigest())
        rows = lambda: capture_native(project).atoms
        calls = []
        def validate(kind, header, component, body):
            calls.append((kind, component, body))
        values = {'template': template, 'container': {'atom': 'AN-T-1'} if contained else {'component': 'C00'},
                  'lens': 'SPEC', 'body': '\n## Summary\n\nExample\n'}
        before = self.files(project)
        if contained:
            with self.assertRaises(InputError):
                create_draft(project, {'newAtom': values}, current_rows=rows(),
                             validate_project_spec_model=validate)
            self.assertEqual(before, self.files(project))
            return
        self._check_spec_lifecycle(project, template, values, rows, validate, calls, before)

    def _check_spec_lifecycle(self, project, template, values, rows, validate, calls, before):
        carrier_root = project.control_root
        if template == 'axiom':
            for invalid in ({'tier': -1}, {'lens': 'DES'}, {'container': {'component': 'C9'}}):
                with self.subTest(invalid=invalid), self.assertRaises(InputError):
                    create_draft(project, {'newAtom': {**values, **invalid}}, current_rows=rows(),
                                 validate_project_spec_model=validate)
            self.assertEqual(before, self.files(project))
        created = create_draft(project, {'newAtom': values}, current_rows=rows(),
                               validate_project_spec_model=validate)
        self.assertEqual('completed', created['outcome'])
        self.assertEqual([(template, 'C00', values['body'])], calls)
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
        for status, directory in (('active', '_SPEC' if template == 'applicable_principle' else ''), ('archived', '09_archived')):
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
