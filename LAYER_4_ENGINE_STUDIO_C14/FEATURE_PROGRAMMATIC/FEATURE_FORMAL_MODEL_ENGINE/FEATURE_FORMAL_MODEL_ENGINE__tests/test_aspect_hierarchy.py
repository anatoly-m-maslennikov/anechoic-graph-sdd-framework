"""Typed Aspect hierarchy preserves independently authored facts."""
from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import compiler_model_statements


class AspectHierarchyTests(unittest.TestCase):
    def test_independent_collections_and_malformed_inputs(self):
        a = 'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering'
        b = 'PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Product'
        claim = ('from anechoic.formal_claims import declare_entity\n'
                 f'declare_entity(entity_name="Project Structure", structure_paths=({a!r},), aspect_memberships=({b!r},))')
        parsed = parse_native_model_claim(claim)
        self.assertEqual((a, f'({b}) ((INSTANCE_OF)) Aspect'), compiler_model_statements(parsed))
        for value in (None, 1, 'Node', (), ('Node',), ([],), (a, a), ('Atom <+ Aspects <+ X',)):
            bad = {'kind': 'entity', 'arguments': {'entity_name': 'Project Structure', 'structure_paths': value, 'aspect_memberships': ()}}
            if value == ():
                continue
            with self.subTest(value=value), self.assertRaises(ValueError):
                compiler_model_statements(bad)
        for bad in (claim.replace(repr(a), '"Node"'), claim.replace(repr(b), '["x"]'),
                    claim.replace(repr(b) + ',', repr(b) + ',' + repr(b) + ',')):
            with self.assertRaises(ValueError):
                parse_native_model_claim(bad)

if __name__ == '__main__':
    unittest.main()
