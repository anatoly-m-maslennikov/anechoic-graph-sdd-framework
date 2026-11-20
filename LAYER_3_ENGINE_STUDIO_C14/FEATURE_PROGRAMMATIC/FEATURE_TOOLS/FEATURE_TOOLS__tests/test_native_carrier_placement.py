import unittest

from native_carrier_placement import native_carrier_path, native_ticket_label


def header(family='SPEC', template=None, lens='SPEC', status='active', container=None):
    context = {}
    if template:
        context['template'] = template
    if lens and family == 'SPEC':
        context['lens'] = lens
    structure = {'container': container or {'component': 'C1'}}
    if family == 'TKT':
        structure['priority'] = 2
    return {'atom_family': family, 'atom_id': f'AN-{dict(SPEC="S", TKT="T", PMETA="P")[family]}-1',
            'structure': structure, 'context': context,
            'state': {'status': status, 'version': 2, 'updated_at': '2026-01-01T00:00:00'}}


def path(h, summary='A useful — summary', owner='/project/unit', owner_template=None):
    return str(native_carrier_path(h, summary, project_root='/project', owner_directory=owner,
                                   owner_template=owner_template))


class NativeCarrierPlacementTests(unittest.TestCase):
    def test_spec_lens_template_and_revisions(self):
        self.assertEqual(path(header(template='component manifest')), '/project/unit/AN-S-1-SPEC-COMPONENT_MANIFEST--a-useful-summary.md')
        self.assertEqual(path(header(lens='DES/DOM')), '/project/unit/__DES/__DOM/AN-S-1-DOM--a-useful-summary.md')
        self.assertEqual(path(header(lens='DES/DOM', status='draft')), '/project/unit/000_draft/AN-S-1@2-draft-DOM--a-useful-summary.md')
        self.assertEqual(path(header(status='archived')), '/project/unit/099_archived/AN-S-1@2-SPEC--a-useful-summary.md')

    def test_pmeta_and_ticket_branches(self):
        self.assertEqual(path(header('PMETA', 'action', status='draft')), '/project/_PMETA/000_draft/AN-P-1@2-draft-ACTION--a-useful-summary.md')
        for template, branch in [('task', 'TASKS'), ('work_report', 'ASSETS'), ('question', 'ISSUES'), ('code_spec_mismatch', 'ISSUES'), ('spec_proposal', 'ASSETS')]:
            with self.subTest(template=template):
                self.assertEqual(path(header('TKT', template, status='done')), f'/project/__TKT/{branch}/done/AN-T-1-{template.upper()}--a-useful-summary.md')

    def test_analysis_owner_and_revisions(self):
        self.assertEqual(path(header('TKT', 'analysis_report')), '/project/__TKT/ASSETS/AN-T-1-ANALYSIS_REPORT--a-useful-summary.md')
        h = header('TKT', 'analysis_report', container={'atom': 'AN-T-4'})
        self.assertEqual(path(h, owner='/project/__TKT/TASKS/backlog', owner_template='task'), '/project/__TKT/TASKS/backlog/AN-T-1-ANALYSIS_REPORT--a-useful-summary.md')
        for template in ('work_report', 'work_log', 'spec_proposal'):
            bound = header('TKT', template, container={'atom': 'AN-T-4'})
            self.assertEqual(path(bound, owner='/project/__TKT/TASKS/backlog', owner_template='task'),
                             f'/project/__TKT/TASKS/backlog/AN-T-1-{template.upper()}--a-useful-summary.md')
        h['state']['status'] = 'archived'
        self.assertEqual(path(h, owner_template='task'), '/project/unit/099_archived/AN-T-1@2-ANALYSIS_REPORT--a-useful-summary.md')
        with self.assertRaisesRegex(ValueError, 'Epic can contain only Tasks, Epics and Work Reports'):
            path(h, owner_template='epic')
        with self.assertRaisesRegex(ValueError, 'Asset can only be bound to a Task'):
            path(h, owner_template='question')
        with self.assertRaises(ValueError):
            path(h)

    def test_epic_bound_work_report(self):
        h = header('TKT', 'work_report', container={'atom': 'AN-T-4'})
        self.assertEqual(path(h, owner='/project/__TKT/TASKS/backlog', owner_template='epic'),
                         '/project/__TKT/TASKS/backlog/ASSETS/AN-T-1-WORK_REPORT--a-useful-summary.md')
        h['state']['status'] = 'archived'
        self.assertEqual(path(h, owner_template='epic'),
                         '/project/unit/ASSETS/099_archived/AN-T-1@2-WORK_REPORT--a-useful-summary.md')

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
        self.assertIsNone(native_ticket_label('task', 'epic'))
        self.assertIsNone(native_ticket_label('task', None))
        self.assertIn('-TASK--', path(header('TKT', 'task', container={'atom': 'AN-T-4'}), owner_template='task'))

    def test_atom_owned_nested_status_and_spec(self):
        container = {'atom': 'AN-T-4'}
        owner = '/project/__TKT/TASKS/epic/task'
        for status, folder, marker in [('backlog', 'backlog', 'AN-T-1'),
                                       ('draft', '000_draft', 'AN-T-1@2-draft'),
                                       ('archived', '099_archived', 'AN-T-1@2')]:
            with self.subTest(status=status):
                h = header('TKT', 'task', status=status, container=container)
                self.assertEqual(path(h, owner=owner, owner_template='task'),
                                 f'{owner}/{folder}/{marker}-TASK--a-useful-summary.md')
        self.assertEqual(path(header(lens='DES/DOM', container=container), owner=owner),
                         f'{owner}/__DES/__DOM/AN-S-1-DOM--a-useful-summary.md')
        self.assertEqual(path(header('PMETA', 'action', status='draft', container=container), owner=owner),
                         f'{owner}/000_draft/AN-P-1@2-draft-ACTION--a-useful-summary.md')

    def test_unsupported_inputs_fail(self):
        for summary in ['—', 'résumé', '']:
            with self.subTest(summary=summary), self.assertRaises(ValueError):
                path(header(), summary)
        with self.assertRaises(ValueError):
            path(header('TKT', 'unknown'))
        self.assertEqual(path(header(container={'atom': 'AN-S-2'})), '/project/unit/AN-S-1-SPEC--a-useful-summary.md')
        self.assertEqual(path(header('PMETA', status='draft')), '/project/_PMETA/000_draft/AN-P-1@2-draft--a-useful-summary.md')


if __name__ == '__main__':
    unittest.main()
