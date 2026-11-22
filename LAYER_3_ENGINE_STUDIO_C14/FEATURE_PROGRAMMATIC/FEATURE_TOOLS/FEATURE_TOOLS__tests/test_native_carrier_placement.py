import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_carrier_placement__pub import native_carrier_path, native_ticket_label


def header(family='SPEC', template=None, lens='SPEC', status='active', container=None):
    context = {}
    if template:
        context['template'] = template
    if lens and family == 'SPEC':
        context['lens'] = lens
    structure = {'container': container or {'component': 'C1'}}
    if family == 'TKT':
        structure['priority'] = 2
    return {'atom_family': family, 'atom_id': f'AN-{dict(SPEC="S", TKT="T", PROJECT_CONFIG="P", PMETA="P")[family]}-1',
            'structure': structure, 'context': context,
            'state': {'status': status, 'version': 2, 'updated_at': '2026-01-01T00:00:00'}}


def path(h, summary='A useful — summary', owner='/project/unit', owner_template=None):
    return str(native_carrier_path(h, summary, project_root='/project', owner_directory=owner,
                                   owner_template=owner_template))


class NativeCarrierPlacementTests(unittest.TestCase):
    def test_spec_lens_template_and_revisions(self):
        self.assertEqual(path(header(template='component manifest')), '/project/unit/AN-S-1-SPEC-COMPONENT_MANIFEST--a-useful-summary.md')
        self.assertEqual(path(header(lens='DES/DOM')), '/project/unit/__DES/__DOM/AN-S-1-DOM--a-useful-summary.md')
        self.assertEqual(path(header(lens='DES/DOM', status='draft')), '/project/unit/01_draft/AN-S-1@2-draft-DOM--a-useful-summary.md')
        self.assertEqual(path(header(status='archived')), '/project/unit/09_archived/AN-S-1@2-SPEC--a-useful-summary.md')

    def test_current_spec_tiers_use_owner_root_and_keep_lens_token(self):
        for tier in (0, 1, 2):
            with self.subTest(tier=tier):
                h = header(lens='DES/DOM')
                h['structure']['tier'] = tier
                self.assertEqual(path(h), '/project/unit/AN-S-1-DOM--a-useful-summary.md')
                h['state']['status'] = 'ready'
                self.assertEqual(path(h), '/project/unit/02_ready/AN-S-1-DOM--a-useful-summary.md')
                h['state']['status'] = 'draft'
                self.assertEqual(path(h), '/project/unit/01_draft/AN-S-1@2-draft-DOM--a-useful-summary.md')
        h = header(lens='DES/DOM')
        h['structure']['tier'] = -1
        self.assertEqual(path(h), '/project/AN-S-1-DOM--a-useful-summary.md')
        h['structure']['tier'] = 3
        self.assertEqual(path(h), '/project/unit/__DES/__DOM/AN-S-1-DOM--a-useful-summary.md')

    def test_tier_four_component_manifest_uses_owner_root(self):
        h = header(template='component_manifest')
        h['structure']['tier'] = 4
        self.assertEqual(path(h), '/project/unit/AN-S-1-SPEC-COMPONENT_MANIFEST--a-useful-summary.md')
        h['state']['status'] = 'archived'
        self.assertEqual(path(h), '/project/unit/09_archived/AN-S-1@2-SPEC-COMPONENT_MANIFEST--a-useful-summary.md')

    def test_pmeta_and_ticket_branches(self):
        self.assertEqual(path(header('PMETA', 'action', status='draft')), path(header('PROJECT_CONFIG', 'action', status='draft')))
        self.assertEqual(path(header('PROJECT_CONFIG', 'action', status='draft')), '/project/002_PROJECT_CONFIG/01_draft/AN-P-1@2-draft-ACTION--a-useful-summary.md')
        for template, branch in [('task', 'TASKS'), ('work_report', 'ASSETS'), ('question', 'ISSUES'), ('code_spec_mismatch', 'ISSUES'), ('spec_proposal', 'ASSETS')]:
            with self.subTest(template=template):
                self.assertEqual(path(header('TKT', template, status='done')), f'/project/001_TICKETS/{branch}/done/AN-T-1-{template.upper()}--a-useful-summary.md')

    def test_model_manifest_placement(self):
        for status, folder, marker in [('active', '', 'AN-C-3193'),
                                       ('draft', '01_draft/', 'AN-C-3193@2-draft'),
                                       ('archived', '09_archived/', 'AN-C-3193@2')]:
            h = header('PROJECT_CONFIG', 'model_manifest', status=status, container={'component': 'C00'})
            h['atom_id'] = 'AN-C-3193'
            self.assertEqual(path(h), f'/project/002_PROJECT_CONFIG/CUSTOM_MODEL/{folder}{marker}-MODEL_MANIFEST--a-useful-summary.md')
        h['structure']['container'] = {'component': 'C1'}
        with self.assertRaisesRegex(ValueError, 'Project Component'):
            path(h)

    def test_ticket_queue_and_complete_placement(self):
        self.assertEqual(path(header('TKT', 'task', status='in_queue')),
                         '/project/001_TICKETS/TASKS/AN-T-1-TASK--a-useful-summary.md')
        self.assertEqual(path(header('TKT', 'work_report', status='complete')),
                         '/project/001_TICKETS/ASSETS/08_complete/AN-T-1-WORK_REPORT--a-useful-summary.md')
        attached = header('TKT', 'work_report', status='complete', container={'atom': 'AN-T-4'})
        with self.assertRaisesRegex(ValueError, 'Only detached Assets'):
            path(attached, owner_template='task')
        with self.assertRaisesRegex(ValueError, 'Only detached Assets'):
            path(header('TKT', 'task', status='complete'))

    def test_analysis_owner_and_revisions(self):
        self.assertEqual(path(header('TKT', 'analysis_report')), '/project/001_TICKETS/ASSETS/AN-T-1-ANALYSIS_REPORT--a-useful-summary.md')
        h = header('TKT', 'analysis_report', container={'atom': 'AN-T-4'})
        self.assertEqual(path(h, owner='/project/001_TICKETS/TASKS/backlog', owner_template='task'), '/project/001_TICKETS/TASKS/backlog/ASSETS/AN-T-1-ANALYSIS_REPORT--a-useful-summary.md')
        for template in ('work_report', 'work_log', 'spec_proposal'):
            bound = header('TKT', template, container={'atom': 'AN-T-4'})
            self.assertEqual(path(bound, owner='/project/001_TICKETS/TASKS/backlog', owner_template='task'),
                             f'/project/001_TICKETS/TASKS/backlog/ASSETS/AN-T-1-{template.upper()}--a-useful-summary.md')
        h['state']['status'] = 'archived'
        self.assertEqual(path(h, owner_template='task'), '/project/unit/ASSETS/09_archived/AN-T-1@2-ANALYSIS_REPORT--a-useful-summary.md')
        self.assertEqual(path(h, owner_template='epic'), path(h, owner_template='task'))
        with self.assertRaisesRegex(ValueError, 'Asset can only be bound to a planning Ticket'):
            path(h, owner_template='question')
        with self.assertRaises(ValueError):
            path(h)

    def test_epic_bound_work_report(self):
        h = header('TKT', 'work_report', container={'atom': 'AN-T-4'})
        self.assertEqual(path(h, owner='/project/001_TICKETS/TASKS/backlog', owner_template='epic'),
                         '/project/001_TICKETS/TASKS/backlog/ASSETS/AN-T-1-WORK_REPORT--a-useful-summary.md')
        h['state']['status'] = 'archived'
        self.assertEqual(path(h, owner_template='epic'),
                         '/project/unit/ASSETS/09_archived/AN-T-1@2-WORK_REPORT--a-useful-summary.md')

    def test_epic_contains_tasks_and_epics(self):
        for template in ('task', 'epic'):
            with self.subTest(template=template):
                h = header('TKT', template, container={'atom': 'AN-T-4'})
                if template == 'epic':
                    h['context']['label'] = 'Sub-epic'
                token = 'TASK' if template == 'task' else 'SUB_EPIC'
                self.assertEqual(path(h, owner_template='epic'),
                                 f'/project/unit/AN-T-1-{token}--a-useful-summary.md')

    def test_nested_labels_are_derived_from_direct_owner(self):
        for template, label, token in [('task', 'Subtask', 'SUBTASK'), ('epic', 'Sub-epic', 'SUB_EPIC')]:
            with self.subTest(template=template):
                self.assertEqual(native_ticket_label(template, template), label)
                h = header('TKT', template, container={'atom': 'AN-T-4'})
                h['context']['label'] = label
                self.assertEqual(path(h, owner_template=template),
                                 f'/project/unit/AN-T-1-{token}--a-useful-summary.md')
        self.assertEqual('Task', native_ticket_label('task', 'epic'))
        self.assertEqual('Task', native_ticket_label('task', 'task', 'Epic'))
        self.assertEqual('Sub-epic', native_ticket_label('epic', 'task', 'Sub-epic'))
        self.assertEqual('Task', native_ticket_label('task', None))
        self.assertEqual('Version', native_ticket_label('task', 'task', label='Version'))
        self.assertIn('-TASK--', path(header('TKT', 'task', container={'atom': 'AN-T-4'}), owner_template='task'))

    def test_atom_owned_nested_status_and_spec(self):
        container = {'atom': 'AN-T-4'}
        owner = '/project/001_TICKETS/TASKS/epic/task'
        for status, folder, marker in [('backlog', 'backlog', 'AN-T-1'),
                                       ('draft', '01_draft', 'AN-T-1@2-draft'),
                                       ('archived', '09_archived', 'AN-T-1@2')]:
            with self.subTest(status=status):
                h = header('TKT', 'task', status=status, container=container)
                self.assertEqual(path(h, owner=owner, owner_template='task'),
                                 f'{owner}/{folder}/{marker}-TASK--a-useful-summary.md')
        self.assertEqual(path(header(lens='DES/DOM', container=container), owner=owner),
                         f'{owner}/__DES/__DOM/AN-S-1-DOM--a-useful-summary.md')
        self.assertEqual(path(header('PROJECT_CONFIG', 'action', status='draft', container=container), owner=owner),
                         f'{owner}/01_draft/AN-P-1@2-draft-ACTION--a-useful-summary.md')

    def test_unsupported_inputs_fail(self):
        for summary in ['—', 'résumé', '']:
            with self.subTest(summary=summary), self.assertRaises(ValueError):
                path(header(), summary)
        with self.assertRaises(ValueError):
            path(header('TKT', 'unknown'))
        self.assertEqual(path(header(container={'atom': 'AN-S-2'})), '/project/unit/AN-S-1-SPEC--a-useful-summary.md')
        self.assertEqual(path(header('PROJECT_CONFIG', status='draft')), '/project/002_PROJECT_CONFIG/01_draft/AN-P-1@2-draft--a-useful-summary.md')


if __name__ == '__main__':
    unittest.main()
