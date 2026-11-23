"""Additional Scope extraction preview and admission cases."""
import unittest



from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.repair__tests.test_scope_extraction_repair_gate import (
    copy,
    fixture,
    hashlib,
    rebind_final,
    rebind_original,
)
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.RMED_ATOM_REVIEW__shared import markdown
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.scope_extraction_repair_gate import admit_scope_extraction_subject_recoding
from FEATURE_AGENTIC.FEATURE_PROMPTS.ACTION_PROMPTS.RMED_ATOM_REVIEW.repair.scope_extraction_preview import admit_scope_extraction_preview



class ScopeExtractionPreviewTests(unittest.TestCase):
    def test_exact_span_bound_preview_is_no_write(self):
        data = fixture()
        original = data['context']['sources'][0]
        final = data['proposal']['outputs'][0]['text']
        virtual = original['text'].removesuffix(markdown(original['text'])) + markdown(final)
        before = copy.deepcopy((original, virtual, data['section_mapping']))
        result = admit_scope_extraction_preview(original['binding'], original['text'], virtual,
                                                section_mapping=data['section_mapping'])
        self.assertEqual(result['result'], 'preview')
        self.assertFalse(result['source_mutation_permitted'])
        self.assertEqual(before, (original, virtual, data['section_mapping']))

    def test_every_source_and_proposed_span_is_exact(self):
        for index, field in ((0, 'source_span'), (0, 'proposed_span'), (1, 'source_span'),
                             (1, 'proposed_span'), (2, 'source_span'), (2, 'proposed_span')):
            data = fixture()
            data['section_mapping']['sections'][index][field][0] += 1
            original = data['context']['sources'][0]
            virtual = original['text'].removesuffix(markdown(original['text'])) + markdown(data['proposal']['outputs'][0]['text'])
            with self.subTest(index=index, field=field):
                self.assertEqual(admit_scope_extraction_preview(original['binding'], original['text'], virtual,
                    section_mapping=data['section_mapping'])['result'], 'rejected')

    def test_compound_or_conditional_source_is_fail_closed(self):
        data = fixture()
        original = data['context']['sources'][0]
        for old, new in (('other than a Project Goal Atom', 'other than a Goal or Demand'),
                         ('other than a Project Goal Atom', 'other than a Goal if accepted')):
            raw = original['text'].replace(old, new)
            binding = dict(original['binding'], sha256=hashlib.sha256(raw.encode()).hexdigest())
            with self.subTest(new=new):
                self.assertEqual(admit_scope_extraction_preview(binding, raw, raw,
                    section_mapping=data['section_mapping'])['result'], 'rejected')



class ScopeExtractionRepairGateTests(unittest.TestCase):
    def test_exact_composition_is_candidate_only(self):
        data = fixture()
        before = copy.deepcopy(data)
        result = admit_scope_extraction_subject_recoding(**data)
        self.assertEqual(result['result'], 'candidate')
        self.assertFalse(result['source_mutation_permitted'])
        self.assertEqual(before, data)

    def test_rejects_condition_scope_claim_or_summary_rewrites(self):
        for old, new in (('other than a Project Goal Atom.', 'other than a Goal.'),
                         ('**every** Atom **must**', '**some** Atom **must**'),
                         ('comply with Atom Context.', 'may comply with Atom Context.'),
                         ('# Summary\nAtom rule', '# Summary\nOther rule')):
            data = fixture()
            output = data['proposal']['outputs'][0]
            output['text'] = output['text'].replace(old, new)
            with self.subTest(old=old), self.assertRaises(ValueError):
                admit_scope_extraction_subject_recoding(**data)

    def test_fully_rebound_scope_and_claim_rewrites_reach_extraction_proof(self):
        for old, new in (
                ('Atom other than a Project Goal Atom.', 'Atom other than a Different Goal Atom.'),
                ('comply with Atom Context.', 'conform with Atom Context.')):
            data = fixture()
            data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace(old, new)
            rebind_final(data)
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, 'exact Scope extraction proof rejected'):
                admit_scope_extraction_subject_recoding(**data)

    def test_fully_rebound_compound_source_reaches_fail_closed_grammar(self):
        data = fixture()
        old = 'Atom other than a Project Goal Atom'
        new = 'Atom other than a Goal or Demand'
        data['context']['sources'][0]['text'] = data['context']['sources'][0]['text'].replace(old, new)
        data['proposal']['outputs'][0]['text'] = data['proposal']['outputs'][0]['text'].replace(old, new)
        rebind_original(data)
        rebind_final(data)
        body = markdown(data['context']['sources'][0]['text'])
        selector_start = body.index(new)
        title_end = body.index('\n') + 1
        data['section_mapping']['sections'][1].update(
            source_span=[selector_start, selector_start + len(new)], source_text=new)
        data['section_mapping']['sections'][2]['source_span'] = [title_end, len(body)]
        data['preflight']['identity_assessment']['scope_equivalence'].update(
            source_excerpt=new, final_scope=new + '.')
        with self.assertRaisesRegex(ValueError, 'compound or conditional selectors'):
            admit_scope_extraction_subject_recoding(**data)

