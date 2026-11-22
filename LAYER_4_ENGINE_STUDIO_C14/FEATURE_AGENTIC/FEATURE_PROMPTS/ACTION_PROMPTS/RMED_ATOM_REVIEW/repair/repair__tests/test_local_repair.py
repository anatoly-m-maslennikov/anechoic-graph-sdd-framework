"""Local-profile repair boundaries and compatibility with the existing gate."""
from copy import deepcopy
import unittest

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_repair_gate import inputs, caller_preflight, SOURCE_TEXT
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared import contract, source, RULE_TEXT
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_proposal
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import _local_repair_boundary


def local_inputs(version=6):
    evaluation, proposal, permission = inputs()
    records = [source('mock.md','MOCK-R-001',SOURCE_TEXT), source('rule.md','MOCK-R-002',RULE_TEXT)]
    context = contract.ReviewContext({
        'confidence_threshold':.99,
        'review_constraints':{'report_contract':version,'review_profile':'atom_local'},
        'sources':records, 'candidate_bindings':[records[0]['binding']],
        'authority_bindings':[records[1]['binding']],
    })
    parts = deepcopy(evaluation['parts'])
    for report in parts:
        report.update(contract_version=version,review_profile='atom_local',context_sha256=context.sha256)
        report['checks'] = [r for r in report['checks'] if r['id'] in contract.LOCAL_GROUPS[report['evaluator']]]
        for row in report['checks']: row.pop('subject_inventory',None)
        if version == 7 and report['evaluator'] == 'cce':
            report['evaluator'] = 'writing'
            report['checks'][0]['id'] = 'writing'
    if version == 7:
        for resolution in proposal['resolutions']:
            if resolution['check_id'] == 'cce':
                resolution['check_id'] = 'writing'
    evaluation = contract.merge_evaluations(parts,context=context)
    proposal['context_sha256'] = context.sha256
    return context,evaluation,proposal,permission


class LocalRepair(unittest.TestCase):
    def test_formatting_proposal_is_supported_without_graph_context(self):
        context,evaluation,proposal,permission = local_inputs()
        result = admit_proposal(evaluation,proposal,context=context,permission=permission,
                                preflight=caller_preflight(proposal))
        self.assertEqual(result['result'],'candidate')
        self.assertFalse(result['source_mutation_permitted'])
        self.assertIn('Independent local evaluation',result['next'])
        self.assertNotIn('affected-reference',result['next'])

    def test_contract7_formatting_proposal(self):
        context, evaluation, proposal, permission = local_inputs(7)
        result = admit_proposal(evaluation, proposal, context=context, permission=permission,
                                preflight=caller_preflight(proposal))
        self.assertEqual(result['result'], 'candidate')

    def test_entity_target_change_is_rejected(self):
        context,evaluation,proposal,permission = local_inputs()
        proposal['disposition'] = 'revision'; permission['dispositions'] = ['revision']
        proposal['outputs'][0]['text'] = proposal['outputs'][0]['text'].replace('governs: Atom','governs: Artifact')
        with self.assertRaisesRegex(ValueError,'preserve Subject and relation targets'):
            admit_proposal(evaluation,proposal,context=context,permission=permission,
                           preflight=caller_preflight(proposal))

    def test_target_shape_normalization_can_preserve_values(self):
        proposal = {'source':{'path':'mock.md'},'disposition':'revision'}
        original = SOURCE_TEXT.replace('governs: Atom','governs: [Atom]')
        output = {'path':'mock.md','text':SOURCE_TEXT}
        _local_repair_boundary(proposal,output,original)

    def test_new_relations_or_changed_target_values_are_rejected(self):
        proposal = {'source':{'path':'mock.md'},'disposition':'revision'}
        for addition in ('relations: {relates_to: [MOCK-R-002]}\n',
                         'subjects: {governs: Other}\n'):
            output = {'path':'mock.md','text':SOURCE_TEXT.replace('subjects:\n  governs: Atom\n',addition)}
            with self.subTest(addition=addition), self.assertRaises(ValueError):
                _local_repair_boundary(proposal,output,SOURCE_TEXT)

    def test_identity_changes_and_moves_require_separate_handling(self):
        for disposition,path in (('split','mock.md'),('replacement','mock.md'),('revision','new.md')):
            proposal = {'source':{'path':'mock.md'},'disposition':disposition}
            with self.subTest(disposition=disposition,path=path), self.assertRaisesRegex(ValueError,'separate authorized run'):
                _local_repair_boundary(proposal,{'path':path,'text':SOURCE_TEXT},SOURCE_TEXT)


if __name__ == '__main__':
    unittest.main()
