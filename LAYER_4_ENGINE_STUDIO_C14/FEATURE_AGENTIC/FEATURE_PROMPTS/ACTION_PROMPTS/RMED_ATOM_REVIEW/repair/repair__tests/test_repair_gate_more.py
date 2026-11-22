"""Additional independent repair admission cases."""
import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_repair_gate import BODY, RECODING_OUTPUT_PATH, RECODING_SOURCE_PATH, RECODING_SOURCE_TEXT, caller_preflight, context, inputs, recoding_inputs
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_proposal


class RepairGateTestsMore(unittest.TestCase):
    def gate(self, evaluation, proposal, permission, *, preflight=None):
        return admit_proposal(evaluation, proposal, context=context(), permission=permission,
                              preflight=caller_preflight(proposal) if preflight is None else preflight)


    def test_recoding_admits_only_a_role_echo_type_elision_and_rename(self):
        review_context, evaluation, proposal, permission = recoding_inputs()
        result = admit_proposal(evaluation, proposal, context=review_context, permission=permission,
                                preflight=caller_preflight(proposal))
        self.assertEqual(result['result'], 'candidate')
        self.assertFalse(result['source_mutation_permitted'])
        self.assertEqual(result['outputs'][0]['path'], RECODING_OUTPUT_PATH)


    def test_recoding_rejects_other_metadata_type_or_carrier_changes(self):
        for mutation in ('version', 'summary', 'body', 'updated_at', 'other_metadata',
                         'specialized_type', 'wrong_role', 'type_retained'):
            review_context, evaluation, proposal, permission = recoding_inputs()
            output = proposal['outputs'][0]
            if mutation == 'version':
                output['version'] = 2
                output['text'] = output['text'].replace('version: 1', 'version: 2')
            elif mutation == 'summary':
                proposal['after_summary'] = 'Different Summary'
                output['text'] = output['text'].replace('Atom rule', 'Different Summary')
            elif mutation == 'body':
                output['text'] += '\nExtra text.\n'
            elif mutation == 'updated_at':
                output['text'] = output['text'].replace('2026-09-27T00:00:00Z', '2026-09-26T00:00:00Z')
            elif mutation == 'other_metadata':
                output['text'] = output['text'].replace('atom_id: MOCK-R-001', 'atom_id: MOCK-R-001\nstatus: Active')
            elif mutation == 'specialized_type':
                proposal['outputs'][0]['text'] = proposal['outputs'][0]['text'].replace(
                    'content_role: Requirement\n', 'content_role: Requirement\ntype: Boundary\n')
            elif mutation == 'wrong_role':
                proposal['outputs'][0]['text'] = proposal['outputs'][0]['text'].replace(
                    'content_role: Requirement\n', 'content_role: Evaluation\ntype: Evaluation\n')
            else:
                output['text'] = RECODING_SOURCE_TEXT
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit_proposal(evaluation, proposal, context=review_context, permission=permission,
                               preflight=caller_preflight(proposal))


    def test_recoding_requires_exact_destination_permission_and_carrier_only_assessment(self):
        review_context, evaluation, proposal, permission = recoding_inputs()
        permission['paths'] = [RECODING_SOURCE_PATH]
        with self.assertRaisesRegex(ValueError, 'path'):
            admit_proposal(evaluation, proposal, context=review_context, permission=permission,
                           preflight=caller_preflight(proposal))
        review_context, evaluation, proposal, permission = recoding_inputs()
        preflight = caller_preflight(proposal)
        preflight['identity_assessment']['classification'] = 'refinement'
        with self.assertRaisesRegex(ValueError, 'identity'):
            admit_proposal(evaluation, proposal, context=review_context, permission=permission,
                           preflight=preflight)


    def test_replacement_requires_new_identity_and_explicit_destination(self):
        evaluation, proposal, permission = inputs()
        proposal.update(disposition='replacement',after_summary='New navigation')
        proposal['outputs'][0].update(path='new.md',atom_id='MOCK-R-003',version=1,
            text=proposal['outputs'][0]['text'].replace('Atom rule','New navigation').replace('MOCK-R-001','MOCK-R-003'))
        permission.update(paths=['mock.md','new.md'],dispositions=['replacement'])
        result = self.gate(evaluation, proposal, permission)
        self.assertEqual(result['result'],'candidate')
        self.assertFalse(result['source_mutation_permitted'])
        proposal['outputs'][0]['atom_id'] = 'MOCK-R-001'
        with self.assertRaises(ValueError):
            self.gate(evaluation,proposal,permission)


    def test_caller_preflight_requires_current_bindings_and_budget(self):
        evaluation, proposal, permission = inputs()
        with self.assertRaisesRegex(ValueError, 'preflight'):
            admit_proposal(evaluation, proposal, context=context(), permission=permission)
        for mutation in ('source', 'context', 'provenance', 'attempt'):
            preflight = caller_preflight(proposal)
            if mutation == 'source':
                preflight['source'] = dict(preflight['source'], sha256='0' * 64)
            elif mutation == 'context':
                preflight['context_sha256'] = '0' * 64
            elif mutation == 'provenance':
                preflight['provenance'] = ''
            else:
                preflight.update(attempt=1, retry_budget=0)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.gate(evaluation, proposal, permission, preflight=preflight)
        self.assertEqual(self.gate(evaluation, proposal, permission,
                                   preflight=caller_preflight(proposal, attempt=0, retry_budget=0))['result'],
                         'candidate')


    def test_identity_assessment_is_external_and_exact(self):
        evaluation, proposal, permission = inputs()
        for mutation in ('missing', 'classification', 'outputs'):
            preflight = caller_preflight(proposal)
            if mutation == 'missing':
                del preflight['identity_assessment']
            elif mutation == 'classification':
                preflight['identity_assessment']['classification'] = 'revision'
            else:
                preflight['identity_assessment']['outputs'][0]['sha256'] = '0' * 64
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'identity'):
                self.gate(evaluation, proposal, permission, preflight=preflight)
        proposal['identity_assessment'] = caller_preflight(proposal)['identity_assessment']
        with self.assertRaisesRegex(ValueError, 'self-attest'):
            self.gate(evaluation, proposal, permission)


    def test_assessment_uses_canonical_change_class_not_fixer_disposition(self):
        evaluation, proposal, permission = inputs()
        for classification in ('formatting', 'revision', 'split', 'refinement', 'semantic_revision'):
            preflight = caller_preflight(proposal)
            preflight['identity_assessment']['classification'] = classification
            with self.subTest(classification=classification), self.assertRaisesRegex(ValueError, 'identity'):
                self.gate(evaluation, proposal, permission, preflight=preflight)
        self.assertEqual(self.gate(evaluation, proposal, permission)['result'], 'candidate')


    def test_revision_version_is_driven_by_external_assessment_class(self):
        evaluation, proposal, permission = inputs()
        proposal['disposition'] = 'revision'
        proposal['outputs'][0].update(version=2,
            text=proposal['outputs'][0]['text'].replace('version: 1', 'version: 2'))
        permission['dispositions'] = ['revision']
        preflight = caller_preflight(proposal)
        preflight['identity_assessment']['classification'] = 'semantic_revision'
        self.assertEqual(self.gate(evaluation, proposal, permission,
            preflight=preflight)['result'], 'candidate')
        preflight = caller_preflight(proposal)
        preflight['identity_assessment']['classification'] = 'refinement'
        with self.assertRaisesRegex(ValueError, 'refinement must preserve version'):
            self.gate(evaluation, proposal, permission, preflight=preflight)

        proposal['outputs'][0].update(version=1,
            text=proposal['outputs'][0]['text'].replace('version: 2', 'version: 1'))
        preflight = caller_preflight(proposal)
        preflight['identity_assessment']['classification'] = 'refinement'
        self.assertEqual(self.gate(evaluation, proposal, permission,
            preflight=preflight)['result'], 'candidate')
        preflight = caller_preflight(proposal)
        preflight['identity_assessment']['classification'] = 'semantic_revision'
        with self.assertRaisesRegex(ValueError, 'semantic revision must increment version once'):
            self.gate(evaluation, proposal, permission, preflight=preflight)
        preflight['identity_assessment']['classification'] = 'carrier_only'
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.gate(evaluation, proposal, permission, preflight=preflight)


    def test_split_uses_replacement_change_class(self):
        evaluation, proposal, permission = inputs()
        original_output = proposal['outputs'][0]
        proposal['disposition'] = 'split'
        proposal['outputs'] = [dict(path=f'new-{i}.md', atom_id=f'MOCK-R-00{i}', version=1,
            text=original_output['text'].replace('MOCK-R-001', f'MOCK-R-00{i}'))
            for i in (3, 4)]
        permission.update(paths=['mock.md', 'new-3.md', 'new-4.md'], dispositions=['split'])
        self.assertEqual(self.gate(evaluation, proposal, permission)['result'], 'candidate')
        preflight = caller_preflight(proposal)
        preflight['identity_assessment']['classification'] = 'split'
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.gate(evaluation, proposal, permission, preflight=preflight)


    def test_replacement_requires_caller_reservation_and_history_plan(self):
        evaluation, proposal, permission = inputs()
        proposal.update(disposition='replacement', after_summary='New navigation')
        proposal['outputs'][0].update(path='new.md', atom_id='MOCK-R-003', version=1,
            text=proposal['outputs'][0]['text'].replace('Atom rule', 'New navigation').replace('MOCK-R-001', 'MOCK-R-003'))
        permission.update(paths=['mock.md', 'new.md'], dispositions=['replacement'])
        for mutation in ('missing', 'bindings', 'plan'):
            preflight = caller_preflight(proposal)
            if mutation == 'missing':
                del preflight['successor_reservations']
            elif mutation == 'bindings':
                preflight['successor_reservations']['bindings'][0]['sha256'] = '0' * 64
            else:
                preflight['successor_reservations']['history_reference_plan'] = ''
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'successor'):
                self.gate(evaluation, proposal, permission, preflight=preflight)
        self.assertEqual(self.gate(evaluation, proposal, permission)['result'], 'candidate')


    def test_permission_dispositions_cannot_use_substring_membership(self):
        for dispositions in ('formattingrevision', {'formatting': True}, ['formatting', 1]):
            evaluation, proposal, permission = inputs()
            permission['dispositions'] = dispositions
            with self.subTest(dispositions=dispositions), self.assertRaises(ValueError):
                self.gate(evaluation, proposal, permission)


    def test_output_binding_requires_carried_identity_and_version(self):
        for header in ('', 'atom_id: MOCK-R-003\n', 'version: 1\n',
                       'atom_id: MOCK-R-003\nversion: true\n'):
            evaluation, proposal, permission = inputs()
            proposal.update(disposition='replacement', after_summary='New navigation')
            permission.update(paths=['mock.md','new.md'], dispositions=['replacement'])
            proposal['outputs'][0].update(path='new.md', atom_id='MOCK-R-003',
                text='---\n' + header + '---\n' + BODY.replace('Atom rule', 'New navigation'))
            with self.subTest(header=header), self.assertRaisesRegex(ValueError, 'frontmatter'):
                self.gate(evaluation, proposal, permission)


    def test_project_root_is_not_an_output_file(self):
        evaluation, proposal, permission = inputs()
        proposal.update(disposition='replacement', after_summary='New navigation')
        permission.update(paths=['mock.md','.'], dispositions=['replacement'])
        proposal['outputs'][0].update(path='.', atom_id='MOCK-R-003',
            text=proposal['outputs'][0]['text'].replace('Atom rule','New navigation').replace('MOCK-R-001','MOCK-R-003'))
        with self.assertRaisesRegex(ValueError, 'path'):
            self.gate(evaluation, proposal, permission)


    def test_forged_merged_pass_is_rejected(self):
        evaluation, proposal, permission = inputs()
        evaluation['checks'][0]['findings'] = []
        with self.assertRaises(ValueError):
            self.gate(evaluation, proposal, permission)


