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


_FIXTURE_1 = (
    "from anechoic.model import Relation\n"
    "from anechoic.formal_claims import Cardi"
    "nality\n"
    "class LINK(Relation):\n"
    "    source_endpoint = {}\n"
    "    target_endpoint = {}\n"
    "    relation.sources_per_target = Cardin"
    "ality(minimum=1, maximum=1)\n"
    "    relation.targets_per_source = Cardin"
    "ality(minimum=0, maximum=2)\n"
)


class TypedPropertyRelationTests(unittest.TestCase):
    def test_relation_axis_domain_comes_from_the_manifest(self):
        for axis, values in (
            ("Transitive", ("no", "yes")),
            ("Symmetric", ("stated", "derived")),
        ):
            text = (
                "from anechoic.model import Property, Relation\n"
                f"class {axis}(Property):\n"
                "    bearer = Relation\n    classification = True\n"
                f"    allowed_values = {values!r}\n"
            )
            subject = f"MODEL//ANECHOIC <+ Graph/Relation >| {axis}"
            args = parse_native_model_claim(
                lower_typed_fields(
                    "manifest_property",
                    text,
                    subject,
                    {"Relation": "Graph/Relation"},
                )
            )["arguments"]
            assert args == {
                "entity_name": "Relation",
                "allowed_axis_values": {axis: values},
            }
            for bad_subject in (
                "MODEL//ANECHOIC <+ Graph/Relation",
                subject + "x",
            ):
                with unittest.TestCase().assertRaises(ValueError):
                    lower_typed_fields(
                        "manifest_property",
                        text,
                        bad_subject,
                        {"Relation": "Graph/Relation"},
                    )
            with unittest.TestCase().assertRaises(ValueError):
                lower_typed_fields(
                    ("manifest_property"),
                    text,
                    subject,
                    {("Relation"): ("Unrelated")},
                )

    def test_rejects_unimported_or_literal_address(self):
        for reference in ["Missing", "Project", '"Node//Artifact//Atom"']:
            text = (
                "from anechoic.model import Property, Atom\n"
                "    class Tier(Property):\n"
                f"        bearer = {reference}\n"
                "        value_format = int\n    "
            )
            with unittest.TestCase().assertRaises(ValueError):
                lower_typed_fields(
                    ("manifest_property"), text, (""), ADDRESSES
                )

    def test_rejects_executable_class_body(self):
        with unittest.TestCase().assertRaises(ValueError):
            lower_typed_fields(
                "manifest_property",
                (
                    "from anechoic.model import Property\n"
                    "class X(Property):\n"
                    "    print(1)\n"
                ),
                "",
                {},
            )

    def test_relation_endpoint_cardinalities(self):
        text = _FIXTURE_1
        claim = lower_typed_fields("manifest_relation", text, "", {})
        args = parse_native_model_claim(claim)["arguments"]
        assert args["sources_per_target"] == {"minimum": 1, "maximum": 1}
        assert args["targets_per_source"] == {"minimum": 0, "maximum": 2}
        with unittest.TestCase().assertRaises(ValueError):
            parse_native_model_claim(
                lower_typed_fields(
                    "manifest_relation",
                    text.replace(
                        ("minimum=0, maximum=2"), ("minimum=3, maximum=2")
                    ),
                    "",
                    {},
                )
            )


if __name__ == "__main__":
    unittest.main()
