import hashlib
import tempfile
import unittest
from pathlib import Path

from SPEC_ENGINE_C75.LAYER_1_SPEC_SOURCES_C83.boundary_model__pub import (
    load_formal_claim,
)
from SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C85.claim_model__pub import (
    normalize_claim,
    validate_declaration,
)


class ClaimSourceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.pin = {'path': 'contract.md', 'atom_id': 'AN-S-1', 'version': 1,
                    'status': 'active', 'container_component': 'C1'}

    def write(self, body):
        content = ('---\natom_family: SPEC\natom_id: AN-S-1\ncontainer: {component: C1}\n'
                   'tier: 0\ncontext: {template: component_contract}\nrelations: {}\n'
                   'state: {status: active, version: 1}\n---\n\n' + body)
        (self.root / self.pin['path']).write_text(content, encoding='utf-8')
        return hashlib.sha256(content.encode()).hexdigest()

    def test_multiple_fences_keep_order_and_all_clauses(self):
        first = "declare_trace_contract(action='run', output='ready', must_effect=(('db', 'saved', {'enabled': True, 'count': 1}),), forbid_effect=('cache',))"
        second = "declare_trace_contract(action='run', output='failed', must_effect=(('log', 'written'),))"
        digest = self.write(f'## Claim\n\n### Formal Claim\n\n```python trace\n{first}\n```\n\n~~~PYTHON TRACE\n{second}\n~~~\n')
        _, declaration, issues = load_formal_claim(self.root, 'C1', 'contract', self.pin)
        self.assertEqual([], issues)
        self.assertEqual(digest, declaration['source']['sha256'])
        self.assertEqual([('python trace', first + '\n'), ('python trace', second + '\n')], declaration['claims'])
        model, error = normalize_claim('contract', declaration, 'C1')
        self.assertIsNone(error)
        cases = model['cases']
        self.assertEqual(['ready', 'failed'], [case['output'] for case in cases])
        self.assertEqual([('db', 'saved', {'enabled': True, 'count': 1})], cases[0]['must_effect'])
        detail = cases[0]['must_effect'][0][2]
        self.assertIs(type(detail['enabled']), bool)
        self.assertIs(type(detail['count']), int)
        self.assertEqual(['cache'], cases[0]['forbid_effect'])
        self.assertEqual([('log', 'written')], cases[1]['must_effect'])

    def test_invalid_forms_keep_source_and_report_failure(self):
        samples = [
            ('python trace', "declare_trace_contract(action='run'", 'issues'),
            ('python unknown', 'anything()', 'issues'),
            ('python trace', "declare_trace_contract(action='run', output='ready', must_effect=[('db', 'saved')])", 'unresolved'),
            ('python trace', "declare_trace_contract(action='run', output='ready', must_effect=(('db', 'saved', {'n': True}),), extra=1)", 'unresolved'),
        ]
        for language, claim, category in samples:
            with self.subTest(claim=claim):
                digest = self.write(f'## Claim\n\n### Formal Claim\n\n```{language}\n{claim}\n```\n')
                _, declaration, _ = load_formal_claim(self.root, 'C1', 'contract', self.pin)
                self.assertEqual([(language, claim + '\n')], declaration['claims'])
                report = validate_declaration(self.root, 'C1', 'contract', self.pin)
                self.assertEqual(digest, report['source']['sha256'])
                self.assertEqual(digest, report[category][0]['source']['sha256'])
                self.assertTrue(report[category][0]['message'])
