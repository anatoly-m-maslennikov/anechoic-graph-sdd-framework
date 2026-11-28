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


def _assert_invalid_relation_selectors(text, names):
    for invalid in (
        text.replace("Relation.target_references()", "str"),
        text.replace(
            ("Relation.subclasses().name"), ("Relation.subclasses()")
        ),
        text.replace(
            ("Relation.subclasses().name"),
            ("Relation.subclasses().inverse_alias"),
        ),
    ):
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "both Relation selectors"
        ):
            lower_typed_fields(
                "manifest_property",
                invalid,
                "",
                ADDRESSES,
                relation_names=names,
            )
    with unittest.TestCase().assertRaisesRegex(
        ValueError, "duplicate or unsupported typed field"
    ):
        lower_typed_fields(
            "manifest_property",
            text + "    dependent_property_cardinality = 1\n",
            "",
            ADDRESSES,
            relation_names=names,
        )


_FIXTURE_2 = (
    "from anechoic.model import Relation\n"
    "class Reference(Relation):\n"
    "    name = 'IS_REFERENCE'\n"
    "    inverse_alias = 'HAS_REFERENCE'\n"
)


_FIXTURE_3 = (
    "from anechoic.formal_claims import decla"
    "re_relation\n"
    "declare_relation(relation_name='DERIVED_"
    "REFERENCE', derived_from='IS_REFERENCE',"
    " source_endpoint={'level': 'instances'},"
    " target_endpoint={'level': 'instances'})"
    "\n"
)


_FIXTURE_1 = (
    "from anechoic.model import Relation\n"
    "class RecursiveReference(Relation):\n"
    "    name = 'RECURSIVE_REFERENCE'\n"
    "    relation.derived_from = 'IS_REFERENC"
    "E'\n"
    "    relation.source_endpoint = {'level':"
    " 'instances'}\n"
    "    relation.target_endpoint = {'level':"
    " 'instances'}\n"
)


_FIXTURE_4 = (
    "from anechoic.model import Property, Ato"
    "m, Project\n"
    "class AtomTier(Property):\n"
    '    name = "Tier"\n'
    "    bearer = Atom.Header\n"
    "    value_format = int\n"
    '    field_options = {"kw_only": True}\n'
    "    allowed_values = (0, 1)\n"
    "    applies_to_entity_classes = (Project"
    ",)\n"
)


_FIXTURE_6 = (
    "from anechoic.model import Property, Ato"
    "m, Requirement, Method, Evaluation, Deli"
    "very\n"
    "from anechoic.formal_claims import Cardi"
    "nality\n"
    "class Content(Property):\n"
    "    bearer = Atom\n"
    "    property_occurrence_cardinality = 1\n"
    "    value_cardinality = 0\n"
    "    dependent_property_cardinality = Car"
    "dinality(minimum=0, maximum=None)\n"
    "    dependent_property_name_format = str"
    "\n"
    "    recursive_dependent_property_cardina"
    "lity = Cardinality(minimum=0, maximum=No"
    "ne)\n"
    "    recursive_dependent_property_name_fo"
    "rmat = str\n"
    "    recursive_dependent_property_value_f"
    "ormat = 'markdown'\n"
    "    ordered_dependent_property_roles = ("
    "Requirement, Method, Evaluation, Deliver"
    "y)\n"
    "    ordered_dependent_property_pairs = ("
    "('Summary', 'Claim'), ('Claim', 'Semanti"
    "cs'), ('Semantics', 'Details'))\n"
)


_FIXTURE_5 = (
    "from anechoic.model import Relation, Ato"
    "m, Project\n"
    "class IS_CONTAINED_BY(Relation):\n"
    "    endpoint_pairs = (\n"
    '        {"source_endpoint": {"level": "i'
    'nstances", "entity_paths": (Atom,)},\n'
    '         "target_endpoint": {"level": "i'
    'nstances", "entity_paths": (Project,)}},'
    "\n"
    "    )\n"
    '    inverse_alias = "CONTAINS"\n'
)


class TypedPropertyRelationTests(unittest.TestCase):
    def _relation_inputs(self):
        explicit = _FIXTURE_2
        derived = _FIXTURE_3
        records = [
            (
                "derived",
                "MODEL//ANECHOIC <+ Graph/Relation//DERIVED_REFERENCE",
                derived,
            )
        ]
        typed_derivation = _FIXTURE_1
        derived_scope = (
            "MODEL//ANECHOIC <+ Graph/Relation//RECURSIVE_REFERENCE"
        )
        fields = [
            (
                "reference",
                "MODEL//ANECHOIC <+ Graph/Relation//IS_REFERENCE",
                explicit,
                "manifest_relation",
            ),
            (
                ("recursive"),
                derived_scope,
                typed_derivation,
                ("manifest_relation"),
            ),
        ]
        names = declared_relation_names(records, fields)
        return names, typed_derivation, derived_scope

    def test_atom_relations_use_explicit_relation_names_and_target_references(
        self,
    ):
        text = _ATOM_RELATIONS
        names, typed_derivation, derived_scope = self._relation_inputs()
        claim = lower_typed_fields(
            "manifest_property", text, "", ADDRESSES, relation_names=names
        )
        arguments = parse_native_model_claim(claim)["arguments"]
        assert arguments["allowed_relation_names"] == ("IS_REFERENCE",)
        lowered = lower_typed_fields(
            ("manifest_relation"), typed_derivation, derived_scope, ADDRESSES
        )
        assert (
            parse_native_model_claim(lowered)["arguments"]["derived_from"]
            == "IS_REFERENCE"
        )
        assert arguments["property_occurrence_cardinality"] == {
            "minimum": 0,
            "maximum": 1,
        }
        assert arguments["dependent_property_cardinality"] == 1
        assert arguments["dependent_property_value_cardinality"] == 2
        assert arguments[("dependent_property_value_format")] == (
            "atom_reference"
        )
        assert arguments["value_cardinality"] == 0
        assert arguments["value_format"] == "dict[str, list[str]] | None"
        _assert_invalid_relation_selectors(text, names)

    def test_property_lowering_preserves_constraints_and_refs(self):
        text = _FIXTURE_4
        result = parse_native_model_claim(
            lower_typed_fields("manifest_property", text, "", ADDRESSES)
        )["arguments"]
        assert result["entity_name"] == "Tier"
        assert result["base_path"] == "Node//Artifact//Atom.Header"
        assert result["applies_to_entity_classes"] == (
            "Node//Artifact//Component//Project",
        )
        assert result["allowed_values"] == (0, 1)

    def test_content_constraints_survive_typed_lowering(self):
        text = _FIXTURE_6
        result = parse_native_model_claim(
            lower_typed_fields("manifest_property", text, "", ADDRESSES)
        )["arguments"]
        assert result["dependent_property_cardinality"] == {
            "minimum": 0,
            "maximum": None,
        }
        assert result["dependent_property_name_format"] == "str"
        assert result["recursive_dependent_property_cardinality"] == {
            "minimum": 0,
            "maximum": None,
        }
        assert result["recursive_dependent_property_name_format"] == "str"
        assert result[("recursive_dependent_property_value_format")] == (
            "markdown"
        )
        assert result["ordered_dependent_property_roles"] == (
            "Requirement",
            "Method",
            "Evaluation",
            "Delivery",
        )
        assert result["ordered_dependent_property_pairs"] == (
            ("Summary", "Claim"),
            ("Claim", "Semantics"),
            ("Semantics", "Details"),
        )

    def test_relation_endpoint_pairs_preserve_disjoint_shapes(self):
        text = _FIXTURE_5
        result = parse_native_model_claim(
            lower_typed_fields("manifest_relation", text, "", ADDRESSES)
        )["arguments"]
        assert result[("endpoint_pairs")][0][("source_endpoint")][
            ("entity_paths")
        ] == ("Node//Artifact//Atom",)
        assert result["inverse_alias"] == "CONTAINS"


if __name__ == "__main__":
    unittest.main()
