"""Workbench regressions for native Status and Relation declarations."""
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_model_claim__pub import parse_native_model_claim
from KERNEL_MIXER_C59.content_schema import DeclarationSource
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.workbench_schema_asset import compile_status_groups
from KERNEL_MIXER_C59.relation_declarations import relation_declaration


class NativeModelWorkbenchQualifiers(unittest.TestCase):
    def test_plan_status_group(self):
        plan = '''from anechoic.model import Plan
from anechoic.formal_claims import declare_entity
declare_entity(entity_name="Status", relation_name="IS_PROPERTY_OF", base_path="Atom.Header.State", applies_to_entity_classes=(Plan,), allowed_values=("Backlog", "Done", "Canceled"), status_order_numbers={"Backlog": 1, "Done": 20, "Canceled": 40}, status_groups={"Backlog": "Backlog"})'''
        declaration = parse_native_model_claim(plan)
        source = DeclarationSource('CA-R-1539', 1, 'status.md')
        self.assertEqual(compile_status_groups([(declaration, source)]), (('Plan', 'Backlog', 'Backlog'),))

    def test_relation_derivation_does_not_change_registry_declaration(self):
        for name, base in (('IS_DECLARED_BY', 'GOVERNS'), ('RECURSIVELY_CONTAINS', 'CONTAINS')):
            with self.subTest(name=name):
                code = ('from anechoic.formal_claims import declare_relation\n'
                        f'declare_relation(relation_name={name!r}, source_endpoint={{"level": "instances"}}, '
                        f'target_endpoint={{"level": "instances"}}')
                body = lambda claim: f'## Claim\n\n### Formal Claim\n\n```python\n{claim}\n```\n'
                self.assertEqual(relation_declaration(body(code + f', derived_from={base!r})'), 'source'),
                                 relation_declaration(body(code + ')'), 'source'))
