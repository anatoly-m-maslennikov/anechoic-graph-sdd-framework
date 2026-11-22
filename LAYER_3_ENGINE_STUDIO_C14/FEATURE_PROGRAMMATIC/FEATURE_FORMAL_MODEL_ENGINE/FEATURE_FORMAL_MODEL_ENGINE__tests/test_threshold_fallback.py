"""Threshold format and literal fallback remain static declaration data."""
from pathlib import Path
import unittest

PROGRAMMATIC = Path(__file__).resolve().parents[2]
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim, NativeModelClaimError
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.compiler_claim import compiler_model_statements
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.compiler_claim_fixtures__pub import THRESHOLD as CLAIM
class ThresholdTests(unittest.TestCase):
 def test_constraints_and_fallback(self):
  decl=parse_native_model_claim(CLAIM);self.assertEqual(compiler_model_statements(decl),('Project.Settings.AI Agent Confidence Threshold{::1} :: [int, 0..100]{::1} ?== 90','Project.Settings.AI Agent Confidence Threshold.*[]{::0}'))
 def test_bad_values(self):
  for bad in (CLAIM.replace('fallback_value=90','fallback_value=101'), CLAIM.replace('maximum_value=100','maximum_value=-1')):
   with self.assertRaises(NativeModelClaimError):parse_native_model_claim(bad)
