"""Additional independent repair admission cases."""
import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_layout_repair_gate import (
    copy,
    fixture,
    hashlib,
    rebind,
)


from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_layout_recoding


class LayoutRepairGateTestsMore(unittest.TestCase):
    def test_final_evaluation_requires_separate_exact_review_attestation(self):
        for mutation in ('missing', 'independent', 'hash'):
            data = fixture()
            if mutation == 'missing':
                del data['preflight']['final_review']
            elif mutation == 'independent':
                data['preflight']['final_review']['independent'] = False
            else:
                data['preflight']['final_review']['evaluation_sha256'] = '0' * 64
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'final review'):
                admit_layout_recoding(**data)


    def test_keyed_resource_roles_cannot_be_swapped(self):
        data = fixture()
        for key in ('context', 'final_context'):
            data[key]['resources']['registry'] = dict(path='registry.toml', text='actor = "reviewer"\n',
                sha256=hashlib.sha256(b'actor = "reviewer"\n').hexdigest())
        resources = data['final_context']['resources']
        resources['rules'], resources['registry'] = resources['registry'], resources['rules']
        rebind(data)
        with self.assertRaisesRegex(ValueError, 'authority resources changed'):
            admit_layout_recoding(**data)


    def test_fully_rebound_specialized_type_deletion_remains_rejected(self):
        data = fixture()
        data['context']['sources'][0]['text'] = data['context']['sources'][0]['text'].replace(
            'type: Requirement', 'type: Boundary')
        rebind(data)
        with self.assertRaisesRegex(ValueError, 'role-echo Type elision'):
            admit_layout_recoding(**data)


    def test_final_pass_cannot_be_forged_or_incomplete(self):
        for mutation in ('raw_parts', 'findings', 'gap', 'binding', 'context'):
            data = fixture()
            report = data['final_evaluation']
            if mutation == 'raw_parts':
                report['parts'].pop()
            elif mutation == 'findings':
                report['checks'][0]['findings'] = [data['evaluation']['checks'][1]['findings'][0]]
            elif mutation == 'gap':
                report['coverage_gaps'] = [dict(check_id='scope', kind='layout_dependency', reason='Missing.')]
            elif mutation == 'binding':
                report['source']['sha256'] = '0' * 64
            else:
                report['context_sha256'] = '0' * 64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_layout_recoding(**data)


    def test_original_merged_finding_must_still_match_retained_raw_parts(self):
        data = fixture()
        data['evaluation']['checks'] = copy.deepcopy(data['evaluation']['checks'])
        data['evaluation']['checks'][1]['findings'][1]['proposed_fix'] = 'Different Summary repair interpretation.'
        with self.assertRaisesRegex(ValueError, 'merged evaluation contradicts'):
            admit_layout_recoding(**data)


    def test_every_original_finding_requires_one_honest_resolution(self):
        for mutation in ('missing', 'duplicate', 'unknown', 'blank', 'deferred'):
            data = fixture()
            resolutions = data['proposal']['resolutions']
            if mutation in ('missing', 'deferred'):
                omitted = resolutions.pop()
                if mutation == 'deferred':
                    data['proposal']['deferred_findings'] = [omitted]
            elif mutation == 'duplicate':
                resolutions.append(resolutions[0])
            elif mutation == 'unknown':
                resolutions[0]['finding_index'] = 99
            else:
                resolutions[0]['reason'] = ''
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_layout_recoding(**data)


    def test_changed_output_bytes_and_layout_mapping_are_rejected(self):
        for old, new in (('Atom rule', 'Different Summary'), ('must comply', 'may comply'),
                         ('Atoms.', 'Some Atoms.'), ('## Details\n', '## Details\nAdded prose.\n'),
                         ('governs: Atom', 'governs: Other'), ('version: 1', 'version: 2'),
                         ('content_role: Requirement', 'type: Boundary\ncontent_role: Requirement')):
            data = fixture()
            data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace(old, new)
            with self.subTest(old=old), self.assertRaises(ValueError):
                admit_layout_recoding(**data)
        data = fixture()
        data['section_mapping']['sections'][0]['source_span'][0] = 1
        with self.assertRaises(ValueError):
            admit_layout_recoding(**data)


    def test_exact_path_permission_and_disposition_are_required(self):
        for mutation in ('source_path', 'output_path', 'disposition', 'renamed', 'traversal'):
            data = fixture()
            if mutation in ('source_path', 'output_path'):
                data['permission']['paths'].pop(0 if mutation == 'source_path' else 1)
            elif mutation == 'disposition':
                data['permission']['dispositions'] = ['revision']
            else:
                path = 'other.md' if mutation == 'renamed' else '../other.md'
                data['proposal']['outputs'][0]['path'] = path
                data['permission']['paths'].append(path)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_layout_recoding(**data)


    def test_identity_must_assess_entire_delta_and_scope_with_sufficient_confidence(self):
        for mutation in ('classification', 'confidence', 'independent', 'source', 'scope', 'support', 'context'):
            data = fixture()
            assessment = data['preflight']['identity_assessment']
            if mutation == 'classification':
                assessment['classification'] = 'refinement'
            elif mutation == 'confidence':
                assessment['confidence'] = .98
            elif mutation == 'independent':
                assessment['independent'] = False
            elif mutation == 'source':
                assessment['source'] = data['preflight']['outputs'][0]
            elif mutation == 'scope':
                assessment['scope_equivalence']['result'] = 'uncertain'
            elif mutation == 'support':
                assessment['scope_equivalence']['support'][0]['authority'] = 'UNBOUND@1'
            else:
                assessment['final_context_sha256'] = '0' * 64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_layout_recoding(**data)


    def test_freshness_retry_and_authority_alias_checks_are_mandatory(self):
        for mutation in ('freshness', 'retry', 'aliases', 'unknown_authority', 'resource', 'threshold'):
            data = fixture(alias=True)
            if mutation == 'freshness':
                data['preflight']['freshness']['authority_sha256'] = '0' * 64
            elif mutation == 'retry':
                data['preflight']['attempt'] = 1
            elif mutation == 'aliases':
                data['preflight']['authority_aliases'] = []
            elif mutation == 'unknown_authority':
                data['final_context']['authority_bindings'].pop()
            elif mutation == 'resource':
                data['final_context']['resources']['rules']['sha256'] = '0' * 64
            else:
                data['final_context']['confidence_threshold'] = .98
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_layout_recoding(**data)


