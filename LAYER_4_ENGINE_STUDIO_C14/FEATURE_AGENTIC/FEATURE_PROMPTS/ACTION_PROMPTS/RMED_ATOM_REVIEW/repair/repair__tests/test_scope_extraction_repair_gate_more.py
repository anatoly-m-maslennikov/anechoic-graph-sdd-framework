"""Additional independent repair admission cases."""
import unittest


from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_scope_extraction_repair_gate import (
    add_original_finding,
    fixture,
    rebind_final,
    rebind_original,
)
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_scope_extraction_subject_recoding



class ScopeExtractionRepairGateTestsMore(unittest.TestCase):
    def test_rejects_gap_bypass_reports_freshness_and_nonindependence(self):
        for mutation in ('non_layout_gap', 'final_gap', 'final_freshness', 'identity', 'scope_independence', 'final_review'):
            data = fixture()
            if mutation == 'non_layout_gap':
                data['evaluation']['parts'][0]['coverage_gaps'].append(
                    {'check_id': 'scope', 'kind': 'reviewer_incomplete', 'reason': 'Unresolved.'})
            elif mutation == 'final_gap':
                data['final_evaluation']['coverage_gaps'] = [
                    {'check_id': 'scope', 'kind': 'layout_dependency', 'reason': 'Missing.'}]
            elif mutation == 'final_freshness':
                data['preflight']['final_freshness']['authority_sha256'] = '0' * 64
            elif mutation == 'identity':
                data['preflight']['identity_assessment']['independent'] = False
            elif mutation == 'scope_independence':
                data['preflight']['identity_assessment']['scope_equivalence']['independent'] = False
            else:
                data['preflight']['final_review']['independent'] = False
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_scope_extraction_subject_recoding(**data)


    def test_fully_rebound_cce_finding_cannot_be_withdrawn_by_final_pass(self):
        data = fixture()
        location = next(row for row in data['evaluation']['checks'] if row['id'] == 'subjects')['findings'][0]['location']
        add_original_finding(data, 'cce', {
            'kind': 'violation', 'location': location, 'excerpt': 'comply',
            'reason': 'Synthetic unrelated CCE defect in preserved predicate.',
            'proposed_fix': 'Change the predicate.', 'confidence': 1.0})
        with self.assertRaisesRegex(ValueError, 'unadmitted original finding: cce'):
            admit_scope_extraction_subject_recoding(**data)


    def test_nonrepaired_subject_and_property_findings_reject_after_rebinding(self):
        data = fixture()
        location = next(row for row in data['evaluation']['checks'] if row['id'] == 'subjects')['findings'][0]['location']
        add_original_finding(data, 'subjects', {
            'kind': 'violation', 'entity': 'Atom', 'location': location, 'excerpt': 'Atom',
            'reason': 'Synthetic unsupported Subjects defect.', 'proposed_fix': 'Change GOVERNS.',
            'confidence': 1.0})
        with self.assertRaisesRegex(ValueError, 'unadmitted Subjects finding'):
            admit_scope_extraction_subject_recoding(**data)
        data = fixture()
        add_original_finding(data, 'properties', {
            'kind': 'violation', 'location': 'frontmatter', 'excerpt': 'content_role: Requirement',
            'reason': 'Synthetic unsupported property defect.', 'proposed_fix': 'Change content role.',
            'confidence': 1.0})
        with self.assertRaisesRegex(ValueError, 'unadmitted Properties finding'):
            admit_scope_extraction_subject_recoding(**data)


    def test_real_heading_omissions_and_dep_fix_remain_admitted(self):
        data = fixture()
        result = admit_scope_extraction_subject_recoding(**data)
        self.assertEqual(result['result'], 'candidate')


    def test_r154_and_r920_property_finding_shapes_remain_exactly_admitted(self):
        variants = {
            'R154': {
                '# Summary': 'CA-D-479:# Summary', '## Scope': 'CA-D-479:## Scope',
                '## Claim': 'CA-D-479:## Claim', '## Details': 'CA-D-479:## Details'},
            'R920': {
                '# Summary': 'CA-D-479:Summary', '## Scope': 'CA-D-479:Scope',
                '## Claim': 'CA-D-479:Claim', '## Details': 'CA-D-479:Details'},
        }
        for name, ids in variants.items():
            data = fixture()
            data['context']['sources'][0]['text'] = data['context']['sources'][0]['text'].replace(
                'type: Requirement\n', 'type: "Requirement"\n')
            for part in data['evaluation']['parts']:
                for row in part['checks']:
                    if row['id'] != 'properties':
                        continue
                    row['findings'][0]['excerpt'] = 'type: "Requirement"'
                    for finding in row['findings'][1:]:
                        heading = finding['obligation_id'].removeprefix('CA-D-479:')
                        finding['obligation_id'] = ids[heading]
                    for obligation in row['obligation_resolutions']:
                        heading = obligation['id'].removeprefix('CA-D-479:')
                        obligation['id'] = ids[heading]
            rebind_original(data)
            with self.subTest(report_shape=name):
                self.assertEqual(admit_scope_extraction_subject_recoding(**data)['result'], 'candidate')


    def test_requires_a_real_depends_on_delta_and_exact_scope_evidence(self):
        data = fixture()
        for part in data['evaluation']['parts']:
            for row in part['checks']:
                if row['id'] == 'subjects':
                    row['findings'][0].update(kind='violation', subject_issue='governs',
                                              reason='Synthetic governing mismatch fixture.')
                    row['obligation_resolutions'] = []
        data['context']['sources'][0]['text'] = data['context']['sources'][0]['text'].replace(
            '  governs: Atom\n', '  governs: Atom\n  depends_on: ["Atom Context"]\n')
        rebind_original(data)
        with self.assertRaisesRegex(ValueError, 'actual DEPENDS_ON correction'):
            admit_scope_extraction_subject_recoding(**data)
        data = fixture()
        data['preflight']['identity_assessment']['scope_equivalence']['source_excerpt'] = 'Atom Context'
        with self.assertRaises(ValueError):
            admit_scope_extraction_subject_recoding(**data)


    def test_fully_rebound_governs_change_reaches_dependency_comparator(self):
        data = fixture()
        data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace(
            '  governs: Atom\n', '  governs: Atom Context\n')
        data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace(
            '  depends_on: ["Atom Context"]\n', '  depends_on: ["Atom"]\n')
        rebind_final(data)
        with self.assertRaisesRegex(ValueError, 'preserve GOVERNS'):
            admit_scope_extraction_subject_recoding(**data)


