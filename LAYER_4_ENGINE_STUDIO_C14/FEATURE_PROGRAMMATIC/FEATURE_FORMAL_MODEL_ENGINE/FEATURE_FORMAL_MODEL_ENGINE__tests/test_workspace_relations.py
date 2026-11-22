import unittest
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import WORKSPACE
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.legacy_claim_compiler__pub import compile_python_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim
class WorkspaceRelationTests(unittest.TestCase):
 def test_authored_direction_and_cardinality(self):
  claim = WORKSPACE
  self.assertEqual('View {::1}((IS_CONTAINED_BY)){::1+} Workspace',compile_python_model_claim(claim)[-1])
  good=lint_python_model_claim(claim,declared_addresses=['View','Workspace'],relation_names=['IS_CONTAINED_BY']);self.assertEqual((),good)
  self.assertTrue(lint_python_model_claim(claim,declared_addresses=['Workspace'],relation_names=['IS_CONTAINED_BY']))
  self.assertTrue(lint_python_model_claim(claim,declared_addresses=['View','Workspace'],relation_names=[]))
  with self.assertRaises(ValueError):compile_python_model_claim(claim.replace('"source_cardinality": 1','"source_cardinality": -1'))
 def test_incoming_without_dataclass_contract_fails_closed(self):
  bad = 'from anechoic.formal_claims import declare_entity\ndeclare_entity(entity_name="Workspace", incoming_model_relations=())'
  with self.assertRaises(ValueError): compile_python_model_claim(bad)
if __name__=='__main__':unittest.main()
