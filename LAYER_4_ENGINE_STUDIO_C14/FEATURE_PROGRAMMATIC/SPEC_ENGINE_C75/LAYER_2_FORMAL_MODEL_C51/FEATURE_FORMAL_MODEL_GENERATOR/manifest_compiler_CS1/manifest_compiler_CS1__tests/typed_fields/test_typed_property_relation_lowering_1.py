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
    "from anechoic.model import Relation\n"
    "class LINK(Relation):\n"
    "    source_endpoint = {}\n"
    "    target_endpoint = {}\n"
    "    inverse_alias = 'LINKED_BY'\n"
    "    relation.axes = {'Functional': 'no',"
    " 'Transitive': 'no'}\n"
    "    relation.inverse_axes = {'Functional"
    "': 'no'}\n"
)


_FIXTURE_1 = (
    "from anechoic.model import Relation\n"
    "class REPLACES(Relation):\n"
    "    source_endpoint = {}\n"
    "    target_endpoint = {}\n"
    "    relation.forbidden_status_pairs = "
)


class TypedPropertyRelationTests(unittest.TestCase):
    def test_scoped_status_groups_cover_the_allowed_values(self):
        atom = ADDRESSES["Atom"]
        addresses = ADDRESSES | {
            "Atom.Header.State": atom + ".Header.State",
            "SpecAtom": atom + "//Specification",
        }
        prefix = (
            "from anechoic.model import Atom, Property, SpecAtom\n"
            "class Status(Property):\n"
            "    bearer = Atom.Header.State\n"
            "    property.applies_to = (SpecAtom,)\n"
            "    property.value.allowed = ('draft', 'ready', 'active')\n"
            "    property.value.groups = "
        )
        valid = "{'draft': 'Draft', 'ready': 'Draft', 'active': 'Active'}"
        lowered = lower_typed_fields(
            "manifest_property", prefix + valid, "", addresses
        )
        self.assertEqual(
            {"draft": "Draft", "ready": "Draft", "active": "Active"},
            parse_native_model_claim(lowered)["arguments"]["status_groups"],
        )
        for invalid in (
            valid.replace("'ready': 'Draft', ", ""),
            valid.replace("'ready'", "'unexpected'"),
            valid.replace("'ready'", "'draft'"),
        ):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_native_model_claim(
                    lower_typed_fields(
                        "manifest_property", prefix + invalid, "", addresses
                    )
                )

    def test_relation_axes_use_native_validation(self):
        text = _FIXTURE_2
        args = parse_native_model_claim(
            lower_typed_fields("manifest_relation", text, "", {})
        )["arguments"]
        assert args["axes"] == {"Functional": "no", "Transitive": "no"}
        assert args["inverse_axes"] == {"Functional": "no"}
        for invalid in (
            text.replace("'Functional': 'no'", "'Functional': ''"),
            text.replace("    inverse_alias = 'LINKED_BY'\n", ""),
        ):
            with unittest.TestCase().assertRaises(ValueError):
                parse_native_model_claim(
                    lower_typed_fields(
                        ("manifest_relation"), invalid, (""), {}
                    )
                )
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "duplicate or unsupported"
        ):
            lower_typed_fields(
                "manifest_relation",
                text + "    axes = {'Functional': 'yes'}\n",
                "",
                {},
            )

    def test_relation_forbidden_status_pairs_require_distinct_literal_pairs(
        self,
    ):
        prefix = _FIXTURE_1
        valid = (
            "(('active', 'active'), ('draft', 'active'), ('active', 'draft'))"
        )
        result = parse_native_model_claim(
            lower_typed_fields(("manifest_relation"), prefix + valid, (""), {})
        )
        assert result["arguments"]["forbidden_status_pairs"] == (
            ("active", "active"),
            ("draft", "active"),
            ("active", "draft"),
        )
        for invalid in (
            "()",
            "('active', 'active')",
            "(('active',),)",
            "(('active', 1),)",
            "(('active', ''),)",
            "(('active', ' active'),)",
            "(('active', str),)",
            "[('active', 'active'), ['active', 'active']]",
        ):
            with unittest.TestCase().assertRaisesRegex(
                ValueError, "forbidden_status_pairs"
            ):
                parse_native_model_claim(
                    lower_typed_fields(
                        "manifest_relation", prefix + invalid, "", {}
                    )
                )

    def test_core_relations_fold_and_enforce_endpoint_levels(self):
        relations = (
            (
                "IS_NARROWER_THAN",
                "model_entities",
                "model_entities",
                "HAS_NARROWER",
                "reverse_written_alias",
                "/",
            ),
            (
                "IS_INSTANCE_OF",
                "instances",
                "model_entities",
                "HAS_INSTANCE",
                "written_alias",
                "//",
            ),
        )
        for name, source, target, inverse, alias_key, alias in relations:
            self._check_core_relation(
                name, source, target, inverse, alias_key, alias
            )

    def _check_core_relation(
        self, name, source, target, inverse, alias_key, alias
    ):
        typed = (
            f"from anechoic.model import Relation\nclass {name}(Relation):\n"
            f'    source_endpoint = {{"level": {source!r}}}\n'
            f'    target_endpoint = {{"level": {target!r}}}\n'
            f"    inverse_alias = {inverse!r}\n    {alias_key} = {alias!r}\n"
        )
        legacy = (
            "from anechoic.formal_claims import declare_relation\n"
            f"declare_relation(relation_name={name!r}, "
            f'source_endpoint={{"level": {source!r}}}, '
            f'target_endpoint={{"level": {target!r}}}, '
            f"inverse_alias={inverse!r}, {alias_key}={alias!r})"
        )
        parsed = parse_native_model_claim(
            lower_typed_fields("manifest_relation", typed, "", {})
        )
        assert parsed == parse_native_model_claim(legacy)
        validate_relation_endpoint_levels(parsed, name, source, target)
        validate_relation_endpoint_levels(parsed, inverse, target, source)
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "endpoint levels or kinds"
        ):
            validate_relation_endpoint_levels(
                parsed, name, source, "instances"
            )
        if name == "IS_INSTANCE_OF":
            self._check_instance_relation(name, parsed)

    def _check_instance_relation(self, name, parsed):

        class Node:
            pass

        registry = {name: (parsed["arguments"], False)}
        validate_model_relations(
            Node,
            {name: [Node]},
            {Node: {}},
            {"Node": Node},
            endpoint_registry=registry,
        )
        with unittest.TestCase().assertRaisesRegex(
            ValueError, "endpoint levels or kinds"
        ):
            validate_model_relations(
                Node,
                {name: [Node()]},
                {Node: {}},
                {"Node": Node},
                endpoint_registry=registry,
            )


if __name__ == "__main__":
    unittest.main()
