"""Focused staged regressions for exact Scope extraction plus DEPENDS_ON repair.

These tests exercise an isolated proposal gate only.  They do not bind or
evaluate a real Atom and never permit a source write.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent.parent
ROOT = HERE.parents[5]
REPAIR = HERE
PACKAGE = HERE.parent

from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__shared import body_sections, markdown
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__shared import GROUPS, ReviewContext, merge_evaluations
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair_gate__shared import admit_scope_extraction_preview, authority_digest
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_repair_gate import refreshed
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__tests.RMED_ATOM_REVIEW__tests__shared import RULE_TEXT, part as legacy_part, source


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def source_body():
    return ('# Atom rule\n\n**every** Atom other than a Project Goal Atom **must** '
            'comply with Atom Context.\n')


def final_body():
    return ('# Summary\nAtom rule\n\n## Scope\nAtom other than a Project Goal Atom.\n\n'
            '## Claim\n\n**every** Atom **must** comply with Atom Context.\n\n## Details\n')


def map_for(original, candidate):
    body, proposed = markdown(original), markdown(candidate)
    selector = 'Atom other than a Project Goal Atom'
    claim = '**every** Atom **must** comply with Atom Context.\n'
    title_end = body.index('\n') + 1
    selector_start = body.index(selector)
    summary_end = proposed.index('\n\n## Scope') + 1
    scope_start = proposed.index(selector + '.', proposed.index('## Scope'))
    reduced_claim = '\n' + claim
    claim_start = proposed.index(reduced_claim, proposed.index('## Claim'))
    return {
        'source_body_sha256': hashlib.sha256(body.encode()).hexdigest(),
        'proposed_body_sha256': hashlib.sha256(proposed.encode()).hexdigest(),
        'sections': [
            {'heading': '# Summary', 'source_span': [0, title_end],
             'proposed_span': [0, summary_end], 'state': 'legacy_h1_to_summary_value',
             'provenance': 'Exact original H1 and generated Summary.'},
            {'heading': '## Scope', 'source_span': [selector_start, selector_start + len(selector)],
             'proposed_span': [scope_start, scope_start + len(selector) + 1],
             'state': 'extracted_applicability', 'provenance': 'Exact source selector.',
             'source_text': selector, 'proposed_text': selector + '.'},
            {'heading': '## Claim', 'source_span': [title_end, len(body)],
             'proposed_span': [claim_start, claim_start + len(reduced_claim)],
             'state': 'selector_reduced_to_bearer',
             'provenance': 'The exact original assertion with only its selector reduced.'},
            {'heading': '## Details', 'source_span': None, 'proposed_span': None,
             'state': 'unassessed_absent', 'provenance': 'No Details prose exists.'},
        ],
    }


def rebind_mapping(data):
    """Bind the supplied map to current source/output bytes, without endorsing them."""
    original = data['context']['sources'][0]['text']
    proposed = markdown(data['proposal']['outputs'][0]['text'])
    body = markdown(original)
    mapping = data['section_mapping']
    mapping['source_body_sha256'] = hashlib.sha256(body.encode()).hexdigest()
    mapping['proposed_body_sha256'] = hashlib.sha256(proposed.encode()).hexdigest()
    mapping['sections'][0]['proposed_span'] = [0, proposed.index('\n\n## Scope') + 1]
    scope_start = proposed.index('## Scope\n') + len('## Scope\n')
    scope_end = proposed.index('\n\n## Claim', scope_start)
    mapping['sections'][1]['proposed_span'] = [scope_start, scope_end]
    mapping['sections'][1]['proposed_text'] = proposed[scope_start:scope_end]
    claim_start = proposed.index('## Claim\n') + len('## Claim\n')
    claim_end = proposed.index('\n## Details\n', claim_start)
    mapping['sections'][2]['proposed_span'] = [claim_start, claim_end]


def rebind_final(data):
    """Rebind a synthetic full final review after output-byte mutation."""
    output = data['proposal']['outputs'][0]
    record = data['final_context']['sources'][0]
    record['text'] = output['text']
    record['binding'].update(path=output['path'], atom_id=output['atom_id'], version=output['version'],
                             sha256=hashlib.sha256(output['text'].encode()).hexdigest())
    ctx = ReviewContext(data['final_context'])
    for part in data['final_evaluation']['parts']:
        part.update(source=record['binding'], context_sha256=ctx.sha256,
                    authority_sources=[row['binding'] for row in data['final_context']['sources'][1:]])
    data['final_evaluation'] = merge_evaluations(data['final_evaluation']['parts'], context=ctx)
    original_ctx = ReviewContext(data['context'])
    binding = data['final_evaluation']['source']
    expected = {'source': data['evaluation']['source'], 'context_sha256': original_ctx.sha256,
                'final_context_sha256': ctx.sha256, 'outputs': [binding]}
    data['proposal'].update(source=expected['source'], context_sha256=original_ctx.sha256)
    data['preflight'].update(expected)
    data['preflight']['identity_assessment'].update(expected)
    data['preflight']['final_review'].update(source=binding, context_sha256=ctx.sha256,
                                              evaluation_sha256=digest(data['final_evaluation']))
    data['preflight']['final_freshness'].update(source=binding,
                                                authority_sha256=authority_digest(data['final_context']))
    rebind_mapping(data)


def rebind_original(data):
    """Rebind a synthetic original review after source-byte mutation."""
    record = data['context']['sources'][0]
    record['binding']['sha256'] = hashlib.sha256(record['text'].encode()).hexdigest()
    ctx = ReviewContext(data['context'])
    for part in data['evaluation']['parts']:
        part.update(source=record['binding'], context_sha256=ctx.sha256,
                    authority_sources=[row['binding'] for row in data['context']['sources'][1:]])
    data['evaluation'] = merge_evaluations(data['evaluation']['parts'], context=ctx)
    final_ctx = ReviewContext(data['final_context'])
    expected = {'source': data['evaluation']['source'], 'context_sha256': ctx.sha256,
                'final_context_sha256': final_ctx.sha256, 'outputs': [data['final_evaluation']['source']]}
    data['proposal'].update(source=expected['source'], context_sha256=ctx.sha256)
    data['preflight'].update(expected)
    data['preflight']['identity_assessment'].update(expected)
    data['preflight']['freshness'].update(source=expected['source'],
                                          authority_sha256=authority_digest(data['context']))
    rebind_mapping(data)


def add_original_finding(data, check_id, finding):
    """Add a contract-valid synthetic original finding and rebind its report."""
    for part in data['evaluation']['parts']:
        for row in part['checks']:
            if row['id'] == check_id:
                row.update(status='failed', findings=row['findings'] + [finding])
                part['result'] = 'failed'
                data['proposal']['resolutions'].append({
                    'check_id': check_id, 'finding_index': len(row['findings']) - 1,
                    'reason': 'Synthetic resolution binding for staged negative coverage.'})
    rebind_original(data)


def _legacy_property_findings(row, part):
    row.update(status='failed', findings=[{
        'kind': 'violation', 'location': 'frontmatter', 'excerpt': 'type: Requirement',
        'reason': 'Role echo is not a specialized Type.', 'proposed_fix': 'Omit role echo.',
        'confidence': 1.0}], obligation_resolutions=[])
    for heading in ('# Summary', '## Scope', '## Claim', '## Details'):
        obligation_id = 'CA-D-479:' + heading
        row['findings'].append({
            'kind': 'omission', 'obligation_id': obligation_id, 'location': 'body:preamble',
            'excerpt': f'Absent {heading}', 'reason': 'Registered heading absent locally.',
            'proposed_fix': f'Add {heading}.', 'confidence': 1.0})
        row['obligation_resolutions'].append({
            'id': obligation_id, 'state': 'missing', 'local_required': True,
            'reason': 'Heading absent locally.',
            'support': [{'authority': 'MOCK-R-002@1',
                         'excerpt': 'Required Summary, Scope, Claim and Details headings.'}]})
    part['result'] = 'failed'


def _fixture_report(record, ctx, legacy, *, rule, definition):
    parts = [legacy_part(group) for group in GROUPS]
    sections = body_sections(record['text'])
    claim_location = sections[-1] if legacy else next(x for x in sections if x.endswith('## Claim'))
    for part in parts:
        part.update(contract_version=5, source=record['binding'], context_sha256=ctx.sha256,
                    authority_sources=[rule['binding'], definition['binding']])
        for row in part['checks']:
            row['positive_observations'] = [
                {'location': claim_location, 'excerpt': 'Atom Context.', 'authority': 'MOCK-R-002@1',
                 'rule_excerpt': 'Atom means a governed statement.'}]
            if row['id'] == 'subjects':
                row['subject_inventory']['sections_reviewed'] = sections
                row['subject_inventory']['mentions'][0].update(
                    location=claim_location, excerpt='Atom Context.')
                row['subject_inventory']['mentions'].append({
                    'location': claim_location, 'excerpt': 'Atom Context.', 'entity': 'Atom Context',
                    'resolution': 'resolved', 'resolution_basis': 'identity',
                    'rationale': 'Literal occurrence is bound to the definition.',
                    'definitions': [{'authority': 'MOCK-R-003@1',
                                     'excerpt': 'Atom Context means the governed context in which an Atom is reviewed.'}]})
            if legacy and row['id'] in ('scope', 'claim', 'details', 'governed_entity', 'alignment', 'summary'):
                row.update(status='blocked', positive_observations=[])
                part['coverage_gaps'].append({'check_id': row['id'], 'kind': 'layout_dependency',
                                              'reason': 'Registered section absent.'})
                part['result'] = 'blocked'
            if legacy and row['id'] == 'subjects':
                row.update(status='failed', findings=[{
                    'kind': 'omission', 'obligation_id': 'direct-dependency', 'entity': 'Atom Context',
                    'location': claim_location, 'excerpt': 'Atom Context.',
                    'reason': 'A substantive Atom Context mention lacks its direct dependency.',
                    'proposed_fix': 'Add the direct dependency once.', 'confidence': 1.0}],
                    obligation_resolutions=[{
                        'id': 'direct-dependency', 'state': 'missing', 'local_required': True,
                        'reason': 'The direct dependency is absent locally.',
                        'support': [{'authority': 'MOCK-R-003@1',
                                     'excerpt': 'Substantive mentions require direct dependencies.'}]}])
                part['result'] = 'failed'
            if legacy and row['id'] == 'properties':
                _legacy_property_findings(row, part)
        statuses = [row['status'] for row in part['checks']]
        part['result'] = ('failed' if 'failed' in statuses
                          else 'blocked' if 'blocked' in statuses else 'passed')
    return merge_evaluations(parts, context=ctx)



def _fixture_packets():
    path = 'core/MOCK-R-001-CORE-REQUIREMENT--atom-rule.md'
    header = ('---\natom_id: MOCK-R-001\nversion: 1\n'
              'updated_at: "2026-09-26T00:00:00Z"\nsubjects:\n  governs: Atom\n'
              'content_role: Requirement\ntype: Requirement\n---\n')
    original = source(path, 'MOCK-R-001', header + source_body())
    final_header = refreshed(header.replace('type: Requirement\n', ''))
    final_text = final_header + final_body()
    final_text = final_text.replace('  governs: Atom\n',
                                    '  governs: Atom\n  depends_on: ["Atom Context"]\n')
    final = source(path.replace('-REQUIREMENT--', '--'), 'MOCK-R-001', final_text)
    rule = source('rule.md', 'MOCK-R-002', RULE_TEXT + '\nRequired Summary, Scope, Claim and Details headings.')
    definition = source('atom-context.md', 'MOCK-R-003',
        '---\nstatus: active\ncontent_role: Requirement\nsubjects:\n  governs: Atom Context\n---\n'
        '# Definition\n\nAtom Context means the governed context in which an Atom is reviewed. '
        'Substantive mentions require direct dependencies.\n')
    resources = {'rules': {'path': 'rules.toml', 'text': 'rule = true\n',
                           'sha256': hashlib.sha256(b'rule = true\n').hexdigest()}}
    packet = {'confidence_threshold': .99, 'review_constraints': {'report_contract': 5},
              'sources': [original, rule, definition],
              'authority_bindings': [rule['binding'], definition['binding']],
              'resources': resources,
              'preflight': {'rules': {'state': 'available', 'reason': 'Bound rules.'},
                            'principles': {'state': 'available', 'reason': 'Bound Principles.'}},
              'principle_admissions': [
                  {'binding': rule['binding'], 'applicable_to': [path],
                   'reason': 'Rule applies to the mock carrier.', 'provenance': 'Synthetic fixture.'},
                  {'binding': definition['binding'], 'applicable_to': [path],
                   'reason': 'Definition applies to the mock carrier.', 'provenance': 'Synthetic fixture.'},
              ]}
    final_packet = copy.deepcopy(packet)
    final_packet['sources'][0] = final
    final_packet['principle_admissions'] = [
        {'binding': rule['binding'], 'applicable_to': [final['binding']['path']],
         'reason': 'Rule applies to the mock candidate.', 'provenance': 'Synthetic fixture.'},
        {'binding': definition['binding'], 'applicable_to': [final['binding']['path']],
         'reason': 'Definition applies to the mock candidate.', 'provenance': 'Synthetic fixture.'},
    ]
    return path, original, final, rule, definition, packet, final_packet


def fixture():
    path, original, final, rule, definition, packet, final_packet = _fixture_packets()
    context, final_context = ReviewContext(packet), ReviewContext(final_packet)

    evaluation, final_evaluation = _fixture_report(original, context, True, rule=rule, definition=definition), _fixture_report(final, final_context, False, rule=rule, definition=definition)
    mapping = map_for(original['text'], final['text'])
    proposal = {'source': original['binding'], 'context_sha256': context.sha256,
                'disposition': 'scope_extraction_subject_recoding', 'confidence': .99,
                'before_summary': 'Atom rule', 'after_summary': 'Atom rule',
                'outputs': [{'path': final['binding']['path'], 'atom_id': 'MOCK-R-001', 'version': 1,
                             'text': final['text']}],
                'resolutions': [{'check_id': row['id'], 'finding_index': index,
                                 'reason': 'Resolved by the exact final extraction and dependency correction.'}
                                for row in evaluation['checks'] for index, _ in enumerate(row['findings'])],
                'preservation': ['Exact legacy condition is moved only by the staged extraction proof.']}
    permission = {'paths': [path, final['binding']['path']],
                  'dispositions': ['scope_extraction_subject_recoding'], 'provenance': 'Exact permission.'}
    expected = {'source': original['binding'], 'context_sha256': context.sha256,
                'final_context_sha256': final_context.sha256, 'outputs': [final['binding']]}
    preflight = {**expected, 'provenance': 'Bound current evidence.', 'attempt': 0, 'retry_budget': 0,
                 'authority_aliases': [],
                 'freshness': {'source': original['binding'], 'authority_sha256': authority_digest(packet),
                               'provenance': 'Original source and authority were re-read.'},
                 'final_freshness': {'source': final['binding'],
                                     'authority_sha256': authority_digest(final_packet),
                                     'provenance': 'Final candidate and authority were re-read.'},
                 'final_review': {'source': final['binding'], 'context_sha256': final_context.sha256,
                                  'evaluation_sha256': digest(final_evaluation), 'independent': True,
                                  'provenance': 'Separate final evaluator.'},
                 'identity_assessment': {**expected, 'classification': 'carrier_only',
                    'confidence': .99, 'independent': True, 'provenance': 'Separate full-delta reviewer.',
                    'scope_equivalence': {
                        'result': 'equivalent', 'source_excerpt': 'Atom other than a Project Goal Atom',
                        'final_scope': 'Atom other than a Project Goal Atom.',
                        'independent': True,
                        'reason': 'The exact original selector is the exact final Scope.',
                        'support': [{'authority': 'MOCK-R-002@1',
                                     'excerpt': 'Atom means a governed statement.'}]}}}
    return {'evaluation': evaluation, 'proposal': proposal, 'context': packet,
            'final_evaluation': final_evaluation, 'final_context': final_packet,
            'section_mapping': mapping, 'permission': permission, 'preflight': preflight}













class ScopeExtractionPreviewTests(unittest.TestCase):
    def test_unicode_selector_is_explicitly_unsupported(self):
        data = fixture()
        original = data['context']['sources'][0]
        raw = original['text'].replace('Project Goal', 'Prøject Goal')
        binding = dict(original['binding'], sha256=hashlib.sha256(raw.encode()).hexdigest())
        result = admit_scope_extraction_preview(binding, raw, raw, section_mapping=data['section_mapping'])
        self.assertEqual(result['result'], 'rejected')
        self.assertIn('unsupported source', result['reason'])



if __name__ == '__main__':
    unittest.main()

