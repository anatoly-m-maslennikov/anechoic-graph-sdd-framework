"""Regressions for Role- and Form-qualified native Status declarations."""
import unittest
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import STATUS_PLAN as PLAN
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import NativeModelClaimError, parse_native_model_claim

class NativeStatusQualifiers(unittest.TestCase):
    def test_explicit_none_rejected(self):
        for name in ("status_groups", "applies_to_role", "applies_to_forms"):
            with self.subTest(name=name), self.assertRaises(NativeModelClaimError):
                parse_native_model_claim(PLAN.replace('status_groups={"Backlog": "Backlog"}', name + '=None'))

    def test_plan_group_order_and_graph(self):
        declaration = parse_native_model_claim(PLAN)
        self.assertEqual(declaration["classes"], ())
        self.assertEqual(declaration["arguments"]["applies_to_entity_classes"], ("Plan",))
        self.assertEqual(declaration['arguments']['status_order_numbers'], {'Backlog': 1, 'Done': 20, 'Canceled': 40})
if __name__ == '__main__':
    unittest.main()
