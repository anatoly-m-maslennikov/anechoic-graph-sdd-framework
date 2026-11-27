import unittest
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.FEATURE_FORMAL_MODEL_ENGINE__shared import compiler_model_statements
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    ANALYSIS,
    STATUS_PLAN as PLAN,
)

class JointClaims(unittest.TestCase):
    def test_typed_reference_and_status_qualifiers_and_axes(self):
        typed='''from anechoic.formal_claims import declare_entity
from anechoic.model import NamedSelection
declare_entity(entity_name="Named Selection", relation_name="IS_PROPERTY_OF", base_path="Projection.Source", value_format=NamedSelection, value_cardinality=1)'''
        statements=compiler_model_statements(parse_native_model_claim(typed),model_class_bindings={'NamedSelection':{'Named Selection'}})
        self.assertTrue(any('[Named Selection//]' in statement for statement in statements))
        plan=compiler_model_statements(parse_native_model_claim(PLAN))
        self.assertTrue(any('Status Group == Backlog' in statement for statement in plan))
        analysis=compiler_model_statements(parse_native_model_claim(ANALYSIS))
        self.assertEqual(len(analysis),2)
        role='''from anechoic.formal_claims import declare_entity
from anechoic.model import Atom
class Method(Atom):
    pass
declare_entity(entity_class=Method, entity_name="Method", qualification_property_path="Atom.Header.Context.Role", axes={"Role Order Number": 3})'''
        self.assertTrue(any('Role Order Number == 3' in statement for statement in compiler_model_statements(parse_native_model_claim(role))))
