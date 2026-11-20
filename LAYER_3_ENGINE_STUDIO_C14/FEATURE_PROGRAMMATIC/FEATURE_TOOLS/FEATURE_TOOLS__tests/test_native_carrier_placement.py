import unittest

from native_carrier_placement import native_carrier_path


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
        self.assertEqual(path(header(lens='DES/DOM')), '/project/unit/DES/DOM/AN-S-1-DOM--a-useful-summary.md')
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
        self.assertEqual(path(h, owner_template='task'), '/project/__TKT/TASKS/099_archived/AN-T-1@2-ANALYSIS_REPORT--a-useful-summary.md')
        with self.assertRaisesRegex(ValueError, 'Epic can contain only Tasks'):
            path(h, owner_template='epic')
        with self.assertRaises(ValueError):
            path(h)

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
