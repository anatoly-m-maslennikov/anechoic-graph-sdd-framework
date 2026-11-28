import unittest
from importlib import import_module

_adapter = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared"
)
_compiler = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.manifest_compiler_CS1."
    "typed_property_relation_lowering"
)
_validation = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared"
)
_relations = import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_MODEL_VALIDATION.model_relation_validation"
)
parse_native_model_claim = _adapter.parse_native_model_claim
declared_relation_names = _compiler.declared_relation_names
lower_typed_fields = _compiler.lower_typed_fields
validate_relation_endpoint_levels = (
    _validation.validate_relation_endpoint_levels
)
validate_model_relations = _relations.validate_model_relations


ADDRESSES = {
    "Atom": "Node//Artifact//Atom",
    "Project": "Node//Artifact//Component//Project",
    "Atom.Header": "Node//Artifact//Atom.Header",
    "Atom.Header.AtomID": "Node//Artifact//Atom.Header.Atom ID",
}

_ATOM_RELATIONS = (
    "from anechoic.model import Atom, Propert"
    "y, Relation\n"
    "from anechoic.formal_claims import Cardi"
    "nality\n"
    "class atom_relations(Property):\n"
    "    name = 'Relations'\n"
    "    bearer = Atom.Header\n"
    "    property.cardinality = Cardinality(m"
    "inimum=0, maximum=1)\n"
    "    property.value.cardinality = 0\n"
    "    property.dependent_property.name.all"
    "owed = Relation.subclasses().name\n"
    "    property.dependent_property.cardinal"
    "ity = 1\n"
    "    property.dependent_property.value.ca"
    "rdinality = 2\n"
    "    property.dependent_property.value.fo"
    "rmat = Relation.target_references()\n"
    "    field_options = {'default': None, 'k"
    "w_only': True}\n"
)


_FIXTURE_2 = (
    "from anechoic.model import Property, Ato"
    "m\n"
    "from anechoic.formal_claims import Cardi"
    "nality\n"
    "class Concern(Property):\n"
    "    bearer = Atom.Header\n"
    "    value_format = object\n"
    "    property_occurrence_cardinality = Ca"
    "rdinality(minimum=0, maximum=1)\n"
)


_FIXTURE_3 = (
    "from anechoic.model import Property, Ato"
    "m\n"
    "from anechoic.formal_claims import value"
    "\n"
    "class Tier(Property):\n"
    "    bearer = Atom.Header\n"
    "    value_format = int\n"
)


_FIXTURE_1 = (
    "from anechoic.model import Property, Ato"
    "m\n"
    "class Identifier(Property):\n"
    "    bearer = Atom.Header.AtomID\n"
    "    value_format = str\n"
)


class TypedPropertyRelationTests(unittest.TestCase):
    def test_written_alias_uses_native_parser_validation(self):
        typed = (
            "from anechoic.model import Relation\n"
            "class R(Relation):\n"
            '    written_alias = ""\n'
        )
        with unittest.TestCase().assertRaises(ValueError):
            parse_native_model_claim(
                lower_typed_fields("manifest_relation", typed, "", {})
            )

    def test_cardinality_is_validated_by_native_parser(self):
        text = _FIXTURE_2
        result = parse_native_model_claim(
            lower_typed_fields("manifest_property", text, "", ADDRESSES)
        )["arguments"]
        assert result["property_occurrence_cardinality"] == {
            "minimum": 0,
            "maximum": 1,
        }

    def test_value_forms_and_existing_options(self):
        prefix = _FIXTURE_3
        fixed = parse_native_model_claim(
            lower_typed_fields(
                "manifest_property",
                prefix
                + (
                    "    value = value(fixed=0)\n"
                    "    field_options = {'kw_only': True}\n"
                ),
                "",
                ADDRESSES,
            )
        )["arguments"]
        assert fixed["allowed_values"] == (0,)
        default = parse_native_model_claim(
            lower_typed_fields(
                "manifest_property",
                prefix
                + (
                    "    value = value(default=1)\n"
                    "    allowed_values = (0, 1)\n"
                    "    field_options = {'kw_only': True}\n"
                ),
                "",
                ADDRESSES,
            )
        )["arguments"]
        assert default["field_options"] == {"kw_only": True, "default": 1}
        assert default["allowed_values"] == (0, 1)
        for suffix in (
            "    value = value(fixed=0)\n    allowed_values = (1,)\n",
            (
                "    value = value(default=0)\n"
                "    field_options = {'default_factory': "
                "'dict'}\n"
            ),
        ):
            with unittest.TestCase().assertRaises(ValueError):
                lower_typed_fields(
                    "manifest_property", prefix + suffix, "", ADDRESSES
                )

    def test_dotted_reference_requires_exact_alias_and_preserves_spaces(self):
        text = _FIXTURE_1
        args = parse_native_model_claim(
            lower_typed_fields("manifest_property", text, "", ADDRESSES)
        )["arguments"]
        assert args["base_path"] == "Node//Artifact//Atom.Header.Atom ID"
        with unittest.TestCase().assertRaises(ValueError):
            lower_typed_fields(
                "manifest_property", text, "", {"Atom": ADDRESSES["Atom"]}
            )


if __name__ == "__main__":
    unittest.main()
