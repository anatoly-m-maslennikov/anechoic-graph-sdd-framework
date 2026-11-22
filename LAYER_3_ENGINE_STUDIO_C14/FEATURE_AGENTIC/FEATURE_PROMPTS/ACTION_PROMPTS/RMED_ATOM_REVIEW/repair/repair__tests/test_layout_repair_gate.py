"""Explicit original-to-final layout admission; synthetic judgments are not truth."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent.parent
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_repair_gate import RULE_TEXT, legacy_part, source, refreshed
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.context_builder import body_sections
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.evaluation_contract import ReviewContext, GROUPS, LOCAL_GROUPS, merge_evaluations
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.semantic_boundaries import unavailable_sections
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.layout_repair_gate import admit_layout_recoding, authority_digest


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _fixture_report(record, ctx, legacy, *, rule, contract, with_type, role):
    parts = [legacy_part(group) for group in GROUPS]
    sections = body_sections(record['text'])
    claim_location = next(s for s in sections if s.endswith('## Claim')) if not legacy else sections[1]
    for part in parts:
        part.update(contract_version=contract, source=record['binding'], context_sha256=ctx.sha256,
                    authority_sources=[rule['binding']])
        if contract == 6:
            part['review_profile'] = 'atom_local'
            part['checks'] = [r for r in part['checks'] if r['id'] in LOCAL_GROUPS[part['evaluator']]]
        for row in part['checks']:
            row['positive_observations'] = [dict(location=claim_location, excerpt='Atom must comply.',
                authority='MOCK-R-002@1', rule_excerpt='Atom means a governed statement.')]
            if row['id'] == 'subjects':
                row['subject_inventory']['sections_reviewed'] = sections
                row['subject_inventory']['mentions'][0]['location'] = claim_location
            if legacy and row['id'] in unavailable_sections(record['text']):
                row.update(status='blocked', positive_observations=[])
                part['coverage_gaps'].append(dict(check_id=row['id'], kind='layout_dependency',
                                                  reason='Registered section absent.'))
                part['result'] = 'blocked'
            if legacy and row['id'] == 'properties':
                row.update(status='failed', positive_observations=[], findings=[], obligation_resolutions=[])
                if with_type:
                    row['findings'].append(dict(kind='violation', location='frontmatter',
                        excerpt=f'type: {role}', reason='Role echo is not a specialized Type.',
                        proposed_fix='Omit role echo.', confidence=1.0))
                for heading in ('# Summary', '## Scope', '## Claim', '## Details'):
                    row['findings'].append(dict(kind='omission', obligation_id=heading,
                        location='body:preamble', excerpt=f'Absent {heading}',
                        reason='Required registered heading absent.', proposed_fix=f'Add {heading}.', confidence=1.0))
                    row['obligation_resolutions'].append(dict(id=heading, state='missing', local_required=True,
                        reason='Heading absent locally.', support=[dict(authority='MOCK-R-002@1',
                        excerpt='Required Summary, Scope, Claim and Details headings.')]))
                part['result'] = 'failed'
    return merge_evaluations(parts, context=ctx, allow_layout_gaps=contract == 6)



def _fixture_packets(role, with_type, alias, contract):
    path = f'core/MOCK-R-001-CORE-{role.upper()}--atom-rule.md'
    header = ('---\natom_id: MOCK-R-001\nversion: 1\n'
              'updated_at: "2026-09-26T00:00:00Z"\nsubjects:\n  governs: Atom\n'
              f'content_role: {role}\n' + (f'type: {role}\n' if with_type else '') + '---\n')
    body = '# Atom rule\nAtom must comply.\n'
    original = source(path, 'MOCK-R-001', header + body)
    scope = 'Atoms.'
    final_body = '# Summary\nAtom rule\n\n## Scope\nAtoms.\n\n## Claim\nAtom must comply.\n\n## Details\n'
    final = source(path.replace(f'-{role.upper()}--', '--') if with_type and contract == 5 else path,
                   'MOCK-R-001', refreshed(header.replace(f'type: {role}\n', '')) + final_body)
    rule = source('rule.md', 'MOCK-R-002', RULE_TEXT + '\nRequired Summary, Scope, Claim and Details headings.')
    resources = {'rules': dict(path='rules.toml', text='rule = true\n',
                              sha256=hashlib.sha256(b'rule = true\n').hexdigest())}
    original_packet = dict(confidence_threshold=.99, review_constraints={'report_contract': 5},
        sources=[original, rule], authority_bindings=[rule['binding']], resources=resources,
        preflight={'rules': {'state': 'available', 'reason': 'Exact bound rules supplied.'}})
    final_packet = copy.deepcopy(original_packet)
    final_packet['sources'][0] = final
    if contract == 6:
        for packet, record in ((original_packet, original), (final_packet, final)):
            packet['review_constraints'] = {'report_contract': 6, 'review_profile': 'atom_local'}
            packet['candidate_bindings'] = [record['binding']]
            packet.pop('resources')
            packet['preflight'] = {}
    aliases = []
    if alias:
        original_packet['authority_bindings'].append(original['binding'])
        snapshot = copy.deepcopy(original)
        snapshot['binding']['path'] = 'snapshots/' + path
        final_packet['sources'].append(snapshot)
        final_packet['authority_bindings'].append(snapshot['binding'])
        aliases.append(dict(original=original['binding'], final=snapshot['binding']))
    return path, body, scope, original, final, rule, original_packet, final_packet, aliases


def fixture(*, role='Requirement', with_type=True, alias=False, contract=5):
    path, body, scope, original, final, rule, original_packet, final_packet, aliases = _fixture_packets(
        role, with_type, alias, contract)
    context, final_context = ReviewContext(original_packet), ReviewContext(final_packet)

    evaluation, final_evaluation = _fixture_report(original, context, True, rule=rule, contract=contract, with_type=with_type, role=role), _fixture_report(final, final_context, False, rule=rule, contract=contract, with_type=with_type, role=role)
    title_end = body.index('\n') + 1
    mapping = dict(source_body_sha256=hashlib.sha256(body.encode()).hexdigest(), sections=[
        dict(heading='# Summary', source_span=[0, title_end], state='legacy_h1_to_summary_value', provenance='Exact H1.'),
        dict(heading='## Scope', source_span=None, state='unassessed_author_proposal', provenance='Caller proposal.', proposed_text=scope),
        dict(heading='## Claim', source_span=[title_end, len(body)], state='verbatim_carried', provenance='Exact remaining bytes.'),
        dict(heading='## Details', source_span=None, state='unassessed_absent', provenance='No additional prose.')])
    proposal = dict(source=original['binding'], context_sha256=context.sha256,
        disposition='layout_recoding', confidence=.99, before_summary='Atom rule', after_summary='Atom rule',
        outputs=[dict(path=final['binding']['path'], atom_id='MOCK-R-001', version=1, text=final['text'])],
        resolutions=[dict(check_id=row['id'], finding_index=i, reason='Resolved by the exact final layout/encoding.')
                     for row in evaluation['checks'] for i, _ in enumerate(row['findings'])],
        preservation=['Exact legacy title and all remaining prose are retained.'])
    permission = dict(paths=list(dict.fromkeys([path, final['binding']['path']])),
                      dispositions=['layout_recoding'], provenance='Exact caller permission.')
    preflight = dict(source=original['binding'], context_sha256=context.sha256,
        final_context_sha256=final_context.sha256, outputs=[final['binding']],
        provenance='Caller bound this exact evidence.', attempt=0, retry_budget=0,
        authority_aliases=aliases,
        final_review=dict(source=final['binding'], context_sha256=final_context.sha256,
            evaluation_sha256=digest(final_evaluation), independent=True,
            provenance='Separate final candidate evaluator.'),
        freshness=dict(source=original['binding'], authority_sha256=authority_digest(original_packet),
                       provenance='Caller re-read source, authority and resources.'),
        identity_assessment=dict(source=original['binding'], context_sha256=context.sha256,
            final_context_sha256=final_context.sha256, outputs=[final['binding']],
            classification='carrier_only', confidence=.99, independent=True,
            provenance='Separate original-to-final identity reviewer.',
            scope_equivalence=dict(result='equivalent', source_excerpt='Atom must comply.',
                final_scope=scope, reason='Same population and governed meaning.',
                support=[dict(authority='MOCK-R-002@1', excerpt='Atom means a governed statement.')])) )
    return dict(evaluation=evaluation, proposal=proposal, context=original_packet,
                final_evaluation=final_evaluation, final_context=final_packet,
                section_mapping=mapping, permission=permission, preflight=preflight)


def rebind(data):
    """Keep synthetic reports/assessment consistent while challenging the gate."""
    data['final_context']['sources'][0] = source(data['proposal']['outputs'][0]['path'], 'MOCK-R-001',
                                               data['proposal']['outputs'][0]['text'])
    for packet_key, report_key in (('context', 'evaluation'), ('final_context', 'final_evaluation')):
        packet, report = data[packet_key], data[report_key]
        record = packet['sources'][0]
        record['binding']['sha256'] = hashlib.sha256(record['text'].encode()).hexdigest()
        ctx = ReviewContext(packet)
        for part in report['parts']:
            part.update(source=record['binding'], context_sha256=ctx.sha256)
            part['authority_sources'] = [packet['sources'][1]['binding']]
        data[report_key] = merge_evaluations(report['parts'], context=ctx,
                                             allow_layout_gaps=ctx.report_contract == 6)
    original_ctx, final_ctx = ReviewContext(data['context']), ReviewContext(data['final_context'])
    data['proposal'].update(source=data['evaluation']['source'], context_sha256=original_ctx.sha256)
    expected = dict(source=data['proposal']['source'], context_sha256=original_ctx.sha256,
                    final_context_sha256=final_ctx.sha256, outputs=[data['final_evaluation']['source']])
    data['preflight'].update(expected)
    data['preflight']['identity_assessment'].update(expected)
    data['preflight']['freshness'].update(source=expected['source'],
                                         authority_sha256=authority_digest(data['context']))
    data['preflight']['final_review'].update(source=data['final_evaluation']['source'],
        context_sha256=final_ctx.sha256, evaluation_sha256=digest(data['final_evaluation']))


class LayoutRepairGateTests(unittest.TestCase):
    def test_local_layout_recoding_requires_exact_complete_local_evidence(self):
        data = fixture(contract=6)
        before = copy.deepcopy(data)
        result = admit_layout_recoding(**data)
        self.assertEqual(result['result'], 'candidate')
        self.assertFalse(result['source_mutation_permitted'])
        self.assertEqual(len(result['resolved_layout_gaps']), 4)
        self.assertEqual(before, data)

    def test_local_layout_recoding_rejects_path_change_even_with_permission(self):
        data = fixture(contract=6)
        data['proposal']['outputs'][0]['path'] = 'core/renamed.md'
        data['permission']['paths'].append('core/renamed.md')
        data['final_context']['candidate_bindings'][0]['path'] = 'core/renamed.md'
        rebind(data)
        with self.assertRaisesRegex(ValueError, 'outside-path'):
            admit_layout_recoding(**data)

    def test_local_layout_recoding_rejects_changed_graph_targets(self):
        data = fixture(contract=6)
        data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace('governs: Atom', 'governs: Artifact')
        new_sha = hashlib.sha256(data['proposal']['outputs'][0]['text'].encode()).hexdigest()
        data['final_context']['candidate_bindings'][0]['sha256'] = new_sha
        rebind(data)
        with self.assertRaisesRegex(ValueError, 'preserve Subject'):
            admit_layout_recoding(**data)

    def test_exact_original_to_final_admission_is_no_write_and_preserves_evidence(self):
        for role in ('Requirement', 'Method', 'Delivery'):
            data = fixture(role=role)
            before = copy.deepcopy(data)
            with self.subTest(role=role):
                result = admit_layout_recoding(**data)
                self.assertEqual(result['result'], 'candidate')
                self.assertFalse(result['source_mutation_permitted'])
                self.assertEqual(len(result['resolved_layout_gaps']), 6)
                self.assertEqual(result['original_evaluation_sha256'], digest(data['evaluation']))
                self.assertEqual(result['final_evaluation_sha256'], digest(data['final_evaluation']))
                self.assertIn('saved source', result['next'])
                self.assertEqual(before, data)

    def test_layout_only_and_explicit_unchanged_authority_alias_are_supported(self):
        for options in ({'with_type': False}, {'alias': True}):
            with self.subTest(options=options):
                self.assertEqual(admit_layout_recoding(**fixture(**options))['result'], 'candidate')

    def test_other_or_fabricated_original_gaps_are_rejected(self):
        for kind in ('reviewer_incomplete', 'unresolved_interpretation', 'conflicting_authority', 'missing_context'):
            data = fixture()
            part = data['evaluation']['parts'][2]
            part['coverage_gaps'].append(dict(check_id='scope', kind=kind, reason='Unresolved non-layout evidence.'))
            if kind == 'missing_context':
                part['coverage_gaps'][-1]['context_key'] = 'rules'
            else:
                data['evaluation'] = merge_evaluations(data['evaluation']['parts'], context=ReviewContext(data['context']))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                admit_layout_recoding(**data)

    def test_consistently_assessed_body_and_frontmatter_rewrites_still_reject(self):
        for old, new, error in (('Atom rule', 'Different Summary', 'lossless layout'),
                ('must comply.', 'must comply twice.', 'lossless layout'),
                ('## Details\n', '## Details\nAdditional prose.\n', 'lossless layout'),
                ('content_role: Requirement', 'content_role: "Requirement"', 'frontmatter bytes'),
                ('2026-09-27T00:00:00Z', '2026-09-26T00:00:00Z', 'updated_at'),
                ('content_role: Requirement', 'content_role: Requirement\ntype: Boundary', 'formatting')):
            data = fixture()
            data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace(old, new)
            if old == 'must comply.':
                for part in data['final_evaluation']['parts']:
                    for row in part['checks']:
                        row['positive_observations'][0]['excerpt'] = 'Atom must comply twice.'
            if new.endswith('type: Boundary'):
                data['proposal']['outputs'][0]['path'] = data['proposal']['source']['path']
            rebind(data)
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, error):
                admit_layout_recoding(**data)

    def test_changed_scope_needs_new_exact_equivalence_and_rejects_changed_meaning(self):
        data = fixture()
        data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace('Atoms.', 'Only reviewed Atoms.')
        data['section_mapping']['sections'][1]['proposed_text'] = 'Only reviewed Atoms.'
        rebind(data)
        with self.assertRaisesRegex(ValueError, 'Scope equivalence'):
            admit_layout_recoding(**data)
        data['preflight']['identity_assessment']['scope_equivalence'].update(
            final_scope='Only reviewed Atoms.', result='changed')
        with self.assertRaisesRegex(ValueError, 'Scope equivalence'):
            admit_layout_recoding(**data)

    def test_consistently_bound_authority_or_resource_drift_still_rejects(self):
        for mutation in ('authority', 'resource'):
            data = fixture()
            if mutation == 'authority':
                rule = data['final_context']['sources'][1]
                rule['text'] += '\nChanged applicable rule.\n'
                rule['binding']['sha256'] = hashlib.sha256(rule['text'].encode()).hexdigest()
            else:
                resource = data['final_context']['resources']['rules']
                resource['text'] = 'rule = false\n'
                resource['sha256'] = hashlib.sha256(resource['text'].encode()).hexdigest()
            rebind(data)
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, 'authority'):
                admit_layout_recoding(**data)












if __name__ == '__main__':
    unittest.main()
