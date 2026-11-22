"""Static Atom Status Group filtering for population dependency records."""
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[2]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim,NativeModelClaimError
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.compiler_claim import compiler_model_statements
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.compiler_claim_fixtures__pub import STATUS_GROUPS as CLAIM
ADDRESSES={'Atom','Atom.Content','Atom.Content.Summary','Atom.Header.Identity.ID','Atom.Header.State.Status'}
class StatusGroupTests(unittest.TestCase):
 def test_filtered_dependency_and_rendering(self):
  decl=parse_native_model_claim(CLAIM)
  self.assertEqual((),lint_python_model_claim(CLAIM,declared_addresses=ADDRESSES,relation_names={'IS_PROPERTY_OF'}))
  self.assertEqual(('Atom.Content.Summary{::1} ::{::1}','Atom.Content.Summary.*[]{::0}'),compiler_model_statements(decl))
 def test_invalid_filters_and_missing_paths(self):
  for bad in [CLAIM.replace('"Current", "Backlog", "Archived"','"Current", "NoSuchGroup"'),CLAIM.replace('"Current", "Backlog", "Archived"','"Draft", "Draft"'),CLAIM.replace('"Current", "Backlog", "Archived"','["bad"]'),CLAIM.replace('population_entity_path="Atom"','population_entity_path="Other"'),CLAIM.replace('"status_groups": ("Current", "Backlog", "Archived")','"status_groups": ()')]:
   with self.subTest(bad=bad),self.assertRaises(NativeModelClaimError):parse_native_model_claim(bad)
  for missing in ADDRESSES:
   with self.subTest(missing=missing):
    self.assertTrue(lint_python_model_claim(CLAIM,declared_addresses=ADDRESSES-{missing},relation_names={'IS_PROPERTY_OF'}))
if __name__=='__main__':unittest.main()
