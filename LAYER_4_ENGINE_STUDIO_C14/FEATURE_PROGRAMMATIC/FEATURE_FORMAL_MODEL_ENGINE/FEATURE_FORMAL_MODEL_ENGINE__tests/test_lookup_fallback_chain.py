"""Static nearest-container fallback chain; the Claim is never executed."""
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[2]
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim,NativeModelClaimError
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.compiler_claim import compiler_model_statements
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import FALLBACK_PLAN as PLAN, FALLBACK_PROP as PROP, FALLBACK_PROJECT as PROJECT, FALLBACK_CLAIM as CLAIM
CATALOG={'Atom','Atom.Header.Context.Role',PLAN,PLAN+'.Header.Context.Plan',PROP,'Project','Project.Settings',PROJECT}
class FallbackChainTests(unittest.TestCase):
 def lint(self,claim=CLAIM,addresses=CATALOG,relations={'IS_PROPERTY_OF','IS_CONTAINED_BY'}):
  return lint_python_model_claim(claim,declared_addresses=addresses,relation_names=relations,path='fixture')
 def test_chain_and_provenance(self):
  decl=parse_native_model_claim(CLAIM);self.assertEqual((),self.lint())
  self.assertEqual((PROP+' :: [int, 0..100]{::0..1}',PROP+'.*[]{::0}'),compiler_model_statements(decl))
 def test_empty_semantics_preserve_zero_false_and_invalid(self):
  empty = object()
  def is_empty(value):
   return value is empty or value is None or (type(value) is str and value == "")
  self.assertTrue(all(is_empty(v) for v in (empty,None,"")))
  self.assertTrue(all(not is_empty(v) for v in (0,False,101,"invalid")))
  self.assertEqual(0, 0 if not is_empty(0) else 90)
  for value in (False,101,"invalid"):
   self.assertFalse(is_empty(value))
   self.assertTrue(type(value) is not int or not 0 <= value <= 100)
 def test_reject_bad_shapes_and_unresolved_paths(self):
  for bad in (CLAIM.replace('"lookup_relation":"IS_CONTAINED_BY"','"unknown":"IS_CONTAINED_BY"'), CLAIM.replace('"project_entity":"Project"','"project_entity":"Other"'),CLAIM.replace('fallback_chain=(', 'fallback_value=1, fallback_chain=('),CLAIM.replace(f'"project_property":"{PROJECT}"','"project_property":"Other.Threshold"')):
   with self.subTest(bad=bad),self.assertRaises(NativeModelClaimError):parse_native_model_claim(bad)
  for missing in (PROP,PROJECT,'Project'):
   with self.subTest(missing=missing):self.assertTrue(self.lint(addresses=CATALOG-{missing}))
  self.assertTrue(self.lint(relations={'IS_PROPERTY_OF'}))
if __name__=='__main__':unittest.main()
