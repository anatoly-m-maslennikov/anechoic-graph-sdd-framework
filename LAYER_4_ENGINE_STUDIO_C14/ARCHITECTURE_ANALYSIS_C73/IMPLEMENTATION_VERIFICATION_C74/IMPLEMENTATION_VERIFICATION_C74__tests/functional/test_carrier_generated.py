"""Bounded generated framing cases from the pinned Manifest and Solution.

The carrier comparison tests check the lowered implementation. This suite
derives expectations directly from both Python declarations and runs the
public functions on the witnesses, including the historical bounds defect.
The declarations abstract the path-specific error text.
"""
import hashlib
import json
import unittest
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    frontmatter_bounds, source_body,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared import generate_framing_cases

ROOT = Path(__file__).resolve().parents[5]
BASE = Path('_anechoic_anechoic/LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC_C15/FEATURE_TOOLS_C16')
PINS = {
    'manifest': {'path': (BASE / '01_draft/AN-S-3069@63-draft-SPEC-COMPONENT_MANIFEST--declare-adapters.md').as_posix(),
                 'atom_id': 'AN-S-3069', 'version': 63, 'status': 'draft', 'container_component': 'C16'},
    'solution': {'path': (BASE / 'ADAPTERS_C30/01_draft/AN-S-4742@2-draft-SWD-SOLUTION--extract-the-carrier-body.md').as_posix(),
                 'atom_id': 'AN-S-4742', 'version': 2, 'status': 'draft', 'container_component': 'C30'},
}
GOLDEN = Path(__file__).parent / 'golden_bugs/carrier-crlf-bounds'


def result(bounds_fn, body_fn, raw):
    bounds = bounds_fn(raw)
    try:
        body = list(body_fn(raw, Path('generated.md')))
    except ValueError:
        body = None
    return {'bounds': list(bounds) if bounds is not None else None, 'body': body}


class GeneratedCarrierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        formal = generate_framing_cases(ROOT, 'C30', PINS['manifest'], PINS['solution'])
        cls.operations = formal['operations']
        cls.cases = formal['cases']
        if not cls.cases:
            raise AssertionError('No generated witnesses')

    def test_live_exports_match_both_claims_including_rejections(self):
        self.assertIsInstance(self.operations, list)
        self.assertCountEqual(self.operations, (frontmatter_bounds.__name__, source_body.__name__))
        rejected = 0
        for case in self.cases:
            raw = bytes(case['input'])
            actual = result(frontmatter_bounds, source_body, raw)
            with self.subTest(raw=raw):
                self.assertEqual(actual, case['manifest'])
                self.assertEqual(actual, case['solution'])
            rejected += actual['bounds'] is None and actual['body'] is None
        self.assertGreater(rejected, 0)

    def test_trailing_space_in_closing_delimiter_is_covered(self):
        raw = b'---\r\n\x00\r\n--- \r\n'
        case = next(case for case in self.cases if bytes(case['input']) == raw)
        self.assertEqual(case['manifest'], {'bounds': None, 'body': None})
        self.assertEqual(case['solution'], case['manifest'])

    def test_preserved_old_and_fixed_sources_are_a_negative_control(self):
        metadata = json.loads((GOLDEN / 'case.json').read_text())
        raw = b'---\r\n---\r\n\x00\xff'
        case = next(case for case in self.cases if bytes(case['input']) == raw)
        outcomes = {}
        for version in ('before', 'fixed'):
            path = GOLDEN / metadata[version]['fixture']
            source = path.read_bytes()
            self.assertEqual(hashlib.sha256(source).hexdigest(), metadata[version]['sha256'])
            namespace = {}
            exec(compile(source, str(path), 'exec'), namespace)
            outcomes[version] = result(namespace['frontmatter_bounds'], namespace['source_body'], raw)
        self.assertEqual(case['manifest'], case['solution'])
        self.assertEqual(outcomes['fixed'], case['manifest'])
        self.assertEqual(outcomes['before']['body'], case['manifest']['body'])
        self.assertNotEqual(outcomes['before']['bounds'], case['manifest']['bounds'])
