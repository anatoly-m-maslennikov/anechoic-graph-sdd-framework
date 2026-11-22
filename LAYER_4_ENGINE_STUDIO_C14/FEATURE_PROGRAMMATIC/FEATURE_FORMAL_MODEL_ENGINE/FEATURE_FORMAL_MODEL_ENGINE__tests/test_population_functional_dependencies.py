"""Population constraints remain source-bound structured data, without evaluation."""
from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import NativeModelClaimError, parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.compiler_claim import compiler_model_statements
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim

from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import DEPENDENCIES as CLAIM
ADDRESSES = {'Projection', 'Projection.Form', 'Projection.Scope Unit', 'Projection.ID'}

class PopulationDependenciesTests(unittest.TestCase):
    def lint(self, text=CLAIM, addresses=ADDRESSES):
        return lint_python_model_claim(text, declared_addresses=addresses,
                                      relation_names={'IS_PROPERTY_OF'}, path='fixture')
    def test_exact_ordered_rules_and_provenance(self):
        declaration = parse_native_model_claim(CLAIM)
        self.assertEqual((), self.lint())
        self.assertEqual(('Projection.ID{::1} :: [string]{::1}', 'Projection.ID.*[]{::0}'),
                         compiler_model_statements(declaration))
    def test_lint_requires_exact_bearer_and_every_property(self):
        for missing in ADDRESSES:
            with self.subTest(missing=missing):
                errors = self.lint(addresses=ADDRESSES - {missing} | {'Other.Form', 'Other.Scope Unit', 'Other.ID'})
                self.assertTrue(errors, missing)
        wrong = CLAIM.replace('base_path="Projection"', 'base_path="Other"')
        self.assertTrue(self.lint(wrong, ADDRESSES | {'Other'}))
    def test_reject_malformed_rules(self):
        for bad in (CLAIM.replace('"keys": ("Form", "Scope Unit")', '"keys": ()'),
                    CLAIM.replace('"keys": ("Form", "Scope Unit")', '"keys": ("../Form",)'),
                    CLAIM.replace('"keys": ("Form", "Scope Unit")', '"keys": (" Form",)'),
                    CLAIM.replace('"keys": ("Form", "Scope Unit")', '"keys": ("Form", "Form")'),
                    CLAIM.replace('"dependents": ("ID",)', '"dependent": ("ID",)', 1),
                    CLAIM.replace('base_path="Projection",', '')):
            with self.subTest(bad=bad), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(bad)
if __name__ == '__main__': unittest.main()
