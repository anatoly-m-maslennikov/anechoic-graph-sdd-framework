"""Static typed Node classification domains and membership."""
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_node_lowering import lower_typed_node
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1.typed_property_relation_lowering import lower_typed_fields
from FEATURE_PROGRAMMATIC.FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import _check_node_classifications
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import parse_native_model_claim


class TypedClassificationsTests(unittest.TestCase):
    def test_axis_and_node_membership(self):
        axis = "from anechoic.model import Property, Classification\nclass ArtifactKind(Property):\n    name = 'Artifact Kind'\n    bearer = Classification\n    classification = True\n    allowed_values = ('Artifact', 'Ephemeral')\n"
        scope = 'MODEL//ANECHOIC <+ Graph/Classification >| Artifact Kind'
        claim = lower_typed_fields('manifest_property', axis, scope, {'Classification': 'Graph/Classification'})
        domain = parse_native_model_claim(claim)
        self.assertEqual(domain['arguments']['allowed_classification_values'], {'Artifact Kind': ('Artifact', 'Ephemeral')})
        text = "class Artifact:\n    classifications = {'Artifact Kind': 'Artifact'}\n"
        subject, lowered = lower_typed_node(text, [], 'MODEL//ANECHOIC <+ Graph/Node//Artifact')[0]
        node = parse_native_model_claim(lowered)
        self.assertEqual(node['arguments']['classifications'], {'Artifact Kind': 'Artifact'})
        rows = [('axis', scope, domain), ('node', subject, node)]
        _check_node_classifications(rows, {'node'})
        for value in ('Unknown',):
            bad = {**node, 'arguments': {**node['arguments'], 'classifications': {'Artifact Kind': value}}}
            with self.assertRaisesRegex(ValueError, 'unadmitted Node classification'):
                _check_node_classifications([rows[0], ('node', subject, bad)], {'node'})
        with self.assertRaisesRegex(ValueError, 'ambiguous or invalid'):
            _check_node_classifications([rows[0], rows[0], rows[1]], {'node'})
        with self.assertRaisesRegex(ValueError, 'unadmitted Node classification'):
            _check_node_classifications([rows[1]], {'node'})
        _check_node_classifications([rows[1]], set())
        for replacement in ("('Artifact', 'Artifact')", "('Artifact', compute())", "()"):
            with self.assertRaises(ValueError):
                lower_typed_fields('manifest_property', axis.replace("('Artifact', 'Ephemeral')", replacement), scope, {'Classification': 'Graph/Classification'})
        for mapping in ("{'Artifact Kind': 'Artifact', 'Artifact Kind': 'Ephemeral'}", "{'Artifact Kind': compute()}"):
            with self.assertRaises(ValueError):
                lower_typed_node(text.replace("{'Artifact Kind': 'Artifact'}", mapping), [], subject)
