"""Repair admission tests. No generated candidate is assumed semantically correct."""
import copy
import hashlib
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent.parent
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared import (  # noqa: E402
    contract, gap, part as legacy_part, source, RULE_TEXT, SOURCE_TEXT as SHARED_SOURCE_TEXT)
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.context_builder import markdown  # noqa: E402
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_proposal  # noqa: E402

BODY = markdown(SHARED_SOURCE_TEXT)
SOURCE_TEXT = ('---\nsubjects:\n  governs: Atom\natom_id: MOCK-R-001\nversion: 1\n'
    'updated_at: "2026-09-26T00:00:00Z"\n---\n' + BODY)
RECODING_SOURCE_TEXT = SOURCE_TEXT.replace(
    'subjects:\n  governs: Atom\n',
    'subjects:\n  governs: Atom\ncontent_role: Requirement\ntype: Requirement\n',
)
RECODING_SOURCE_PATH = 'core/MOCK-R-001-CORE-REQUIREMENT--atom-rule.md'
RECODING_OUTPUT_PATH = 'core/MOCK-R-001-CORE--atom-rule.md'


def refreshed(raw):
    return raw.replace('2026-09-26T00:00:00Z', '2026-09-27T00:00:00Z')


def context():
    return contract.ReviewContext({'confidence_threshold': 0.99,
        'review_constraints': {'report_contract': 5}, 'sources': [
        source('mock.md', 'MOCK-R-001', SOURCE_TEXT),
        source('rule.md', 'MOCK-R-002', RULE_TEXT)]})


def recoding_context():
    return contract.ReviewContext({'confidence_threshold': 0.99,
        'review_constraints': {'report_contract': 5}, 'sources': [
        source(RECODING_SOURCE_PATH, 'MOCK-R-001', RECODING_SOURCE_TEXT),
        source('rule.md', 'MOCK-R-002', RULE_TEXT)]})


def legacy_context():
    """A readable v4 record is deliberately not a current repair admission."""
    return contract.ReviewContext({'confidence_threshold': 0.99, 'sources': [
        source('mock.md', 'MOCK-R-001', SOURCE_TEXT),
        source('rule.md', 'MOCK-R-002', RULE_TEXT)]})


def current_part(group, source_binding, review_context):
    result = legacy_part(group)
    result.update(contract_version=5, source=source_binding,
                  context_sha256=review_context.sha256)
    for check in result['checks']:
        check['positive_observations'] = [{
            'location': 'body:5:## Claim', 'excerpt': 'Atom must comply.',
            'authority': 'MOCK-R-002@1',
            'rule_excerpt': 'Atom means a governed statement.',
        }]
    return result


def part(group):
    review_context = context()
    return current_part(group, source('mock.md', 'MOCK-R-001', SOURCE_TEXT)['binding'], review_context)


def inputs():
    parts = [part(group) for group in contract.GROUPS]
    parts[0]['checks'][0].update(status='failed', findings=[dict(
        kind='violation', location='Claim', excerpt='must', reason='Operator not bold',
        proposed_fix='Use **must**', confidence=1.0)])
    parts[0]['result'] = 'failed'
    evaluation = contract.merge_evaluations(parts, context=context())
    proposal = dict(source=evaluation['source'], context_sha256=context().sha256,
        disposition='formatting', confidence=1.0,
        before_summary='Atom rule', after_summary='Atom rule',
        outputs=[dict(path='mock.md', atom_id='MOCK-R-001', version=1,
            text=refreshed(SOURCE_TEXT.replace('must', '**must**')))],
        resolutions=[dict(check_id='cce', finding_index=0,
            reason='Bold the operator without changing the proposition.')],
        preservation=['Preserves the only Claim and Scope.'])
    permission = dict(paths=['mock.md'], dispositions=['formatting'], provenance='Test Operator input')
    return evaluation, proposal, permission


def recoding_inputs():
    review_context = recoding_context()
    source_binding = source(RECODING_SOURCE_PATH, 'MOCK-R-001', RECODING_SOURCE_TEXT)['binding']
    parts = [current_part(group, source_binding, review_context) for group in contract.GROUPS]
    parts[0]['checks'][0].update(status='failed', findings=[dict(
        kind='violation', location='type', excerpt='type: Requirement',
        reason='Ordinary Requirement must omit the role-echo Type.',
        proposed_fix='Remove the redundant Type field and its filename token.', confidence=1.0)])
    parts[0]['result'] = 'failed'
    evaluation = contract.merge_evaluations(parts, context=review_context)
    proposal = dict(source=evaluation['source'], context_sha256=review_context.sha256,
        disposition='recoding', confidence=1.0,
        before_summary='Atom rule', after_summary='Atom rule',
        outputs=[dict(path=RECODING_OUTPUT_PATH, atom_id='MOCK-R-001', version=1,
            text=refreshed(RECODING_SOURCE_TEXT.replace('type: Requirement\n', '')))],
        resolutions=[dict(check_id='cce', finding_index=0,
            reason='Remove only the redundant Requirement Type field.')],
        preservation=['Preserves the complete Markdown body, identity, version and Summary.'])
    permission = dict(paths=[RECODING_SOURCE_PATH, RECODING_OUTPUT_PATH], dispositions=['recoding'],
                      provenance='Test Operator input')
    return review_context, evaluation, proposal, permission


def output_bindings(proposal):
    return [dict(path=output['path'], atom_id=output['atom_id'], version=output['version'],
                 sha256=hashlib.sha256(output['text'].encode()).hexdigest())
            for output in proposal['outputs']]


def caller_preflight(proposal, *, attempt=0, retry_budget=0):
    bindings = output_bindings(proposal)
    result = dict(source=proposal['source'], context_sha256=proposal['context_sha256'],
                  provenance='Synthetic caller re-read current source and authority bindings.',
                  attempt=attempt, retry_budget=retry_budget,
                  identity_assessment=dict(
                      source=proposal['source'], context_sha256=proposal['context_sha256'],
                      classification={'formatting': 'carrier_only', 'recoding': 'carrier_only', 'revision': 'refinement',
                                      'replacement': 'replacement', 'split': 'replacement'}[proposal['disposition']],
                      outputs=copy.deepcopy(bindings),
                      provenance='Synthetic external CA-O-067 assessment for this exact candidate.'))
    if proposal['disposition'] in ('replacement', 'split'):
        result['successor_reservations'] = dict(
            bindings=copy.deepcopy(bindings),
            provenance='Synthetic caller reservation of exact successor bindings.',
            history_reference_plan='Record predecessor/successor bindings and recheck affected references.')
    return result


class RepairGateTests(unittest.TestCase):
    def gate(self, evaluation, proposal, permission, *, preflight=None):
        return admit_proposal(evaluation, proposal, context=context(), permission=permission,
                              preflight=caller_preflight(proposal) if preflight is None else preflight)

    def test_admitted_candidate_is_not_verified_and_inputs_stay_unchanged(self):
        evaluation, proposal, permission = inputs()
        before = copy.deepcopy((evaluation, proposal, permission))
        result = self.gate(evaluation, proposal, permission)
        self.assertEqual(result['result'], 'candidate')
        self.assertFalse(result['source_mutation_permitted'])
        self.assertEqual(before, (evaluation, proposal, permission))

    def test_contract_four_stays_readable_but_cannot_admit_a_new_candidate(self):
        review_context = legacy_context()
        source_binding = source('mock.md', 'MOCK-R-001', SOURCE_TEXT)['binding']
        parts = [legacy_part(group) for group in contract.GROUPS]
        for item in parts:
            item.update(source=source_binding, context_sha256=review_context.sha256)
        parts[0]['checks'][0].update(status='failed', findings=[dict(
            kind='violation', location='Claim', excerpt='must', reason='Operator not bold',
            proposed_fix='Use **must**', confidence=1.0)])
        parts[0]['result'] = 'failed'
        evaluation = contract.merge_evaluations(parts, context=review_context)
        self.assertEqual(evaluation['contract_version'], 4)
        proposal = dict(source=evaluation['source'], context_sha256=review_context.sha256,
            disposition='formatting', confidence=1.0,
            before_summary='Atom rule', after_summary='Atom rule',
            outputs=[dict(path='mock.md', atom_id='MOCK-R-001', version=1,
                text=refreshed(SOURCE_TEXT.replace('must', '**must**')))],
            resolutions=[dict(check_id='cce', finding_index=0,
                reason='Bold the operator without changing the proposition.')],
            preservation=['Preserves the only Claim and Scope.'])
        permission = dict(paths=['mock.md'], dispositions=['formatting'], provenance='Test Operator input')
        with self.assertRaisesRegex(ValueError, 'report contract 5'):
            admit_proposal(evaluation, proposal, context=review_context, permission=permission,
                           preflight=caller_preflight(proposal))

    def test_any_coverage_gap_blocks_proposal(self):
        evaluation, proposal, permission = inputs()
        parts = evaluation['parts']
        parts[1]['checks'][0]['status'] = 'blocked'
        parts[1].update(result='blocked',coverage_gaps=[gap('properties','Missing structure')])
        evaluation = contract.merge_evaluations(parts,context=context())
        self.assertEqual(self.gate(evaluation, proposal, permission)['result'],'blocked')

    def test_changed_source_or_context_is_rejected(self):
        for field, value in [('source',dict(inputs()[1]['source'],sha256='0'*64)),('context_sha256','0'*64)]:
            evaluation, proposal, permission = inputs()
            proposal[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.gate(evaluation, proposal, permission)

    def test_dispositions_paths_and_permission_need_explicit_admission(self):
        for mutation in ('missing','path','disposition','traversal','absolute','secret'):
            evaluation, proposal, permission = inputs()
            if mutation == 'missing':
                permission = {}
            elif mutation == 'path':
                proposal['outputs'][0]['path'] = 'other.md'
            elif mutation == 'disposition':
                proposal['disposition'] = 'replacement'
            else:
                bad = {'traversal':'../mock.md','absolute':'/tmp/mock.md','secret':'x/.env.mock'}[mutation]
                proposal['outputs'][0]['path'] = bad
                permission['paths'].append(bad)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.gate(evaluation, proposal, permission)

    def test_all_findings_need_one_resolution_and_finite_confidence(self):
        for key, value in [('resolutions',[]),('resolutions',inputs()[1]['resolutions']*2),
                           ('confidence',0.98),('confidence',True),('confidence',float('nan'))]:
            evaluation, proposal, permission = inputs()
            proposal[key] = value
            with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                self.gate(evaluation, proposal, permission)

    def test_summary_change_cannot_keep_identity(self):
        evaluation, proposal, permission = inputs()
        proposal.update(after_summary='New navigation',disposition='revision')
        permission['dispositions'].append('revision')
        proposal['outputs'][0].update(version=2,text=proposal['outputs'][0]['text'].replace('Atom rule','New navigation').replace('version: 1', 'version: 2'))
        with self.assertRaisesRegex(ValueError,'Summary'):
            self.gate(evaluation, proposal, permission)

    def test_declared_summary_must_match_real_body(self):
        evaluation, proposal, permission = inputs()
        proposal['outputs'][0]['text'] = proposal['outputs'][0]['text'].replace('Atom rule','Hidden change')
        with self.assertRaisesRegex(ValueError,'Summary'):
            self.gate(evaluation, proposal, permission)

    def test_formatting_requires_a_refreshed_timestamp_and_preserves_other_frontmatter(self):
        for mutation in ('timestamp_unchanged', 'timestamp_reversed', 'extra_metadata'):
            evaluation, proposal, permission = inputs()
            output = proposal['outputs'][0]
            if mutation == 'timestamp_unchanged':
                output['text'] = output['text'].replace('2026-09-27T00:00:00Z', '2026-09-26T00:00:00Z')
            elif mutation == 'timestamp_reversed':
                output['text'] = output['text'].replace('2026-09-27T00:00:00Z', '2026-09-25T00:00:00Z')
            else:
                output['text'] = output['text'].replace(
                    'atom_id: MOCK-R-001', 'atom_id: MOCK-R-001\nstatus: Active')
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'updated_at|formatting'):
                self.gate(evaluation, proposal, permission)

    def test_formatting_keeps_version(self):
        evaluation, proposal, permission = inputs()
        proposal['outputs'][0]['version'] = 2
        proposal['outputs'][0]['text'] = proposal['outputs'][0]['text'].replace('version: 1', 'version: 2')
        with self.assertRaisesRegex(ValueError,'formatting'):
            self.gate(evaluation, proposal, permission)

    def test_revision_keeps_path(self):
        evaluation, proposal, permission = inputs()
        proposal['disposition'] = 'revision'
        proposal['outputs'][0].update(path='renamed.md', version=2,
            text=proposal['outputs'][0]['text'].replace('version: 1', 'version: 2'))
        permission.update(paths=['mock.md', 'renamed.md'], dispositions=['revision'])
        with self.assertRaisesRegex(ValueError, 'path'):
            self.gate(evaluation, proposal, permission)
















if __name__ == '__main__':
    unittest.main()
