import importlib

fixtures = importlib.import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests.declarations."
    "_declaration_fixtures"
)
CLAIM = fixtures.CLAIM
carrier = fixtures.carrier
select_model_claims = fixtures.select_model_claims
_check_relation_references = fixtures._check_relation_references
_class_property_aliases = fixtures._class_property_aliases
build_relation_declaration_catalog = (
    fixtures.build_relation_declaration_catalog
)
relation_setup = fixtures.relation_setup
property_setup = fixtures.property_setup
inheritance_setup = fixtures.inheritance_setup
registry_native = fixtures.registry_native


class DeclarationCases0:
    def test_population_keys_resolve_on_qualified_model_owner(self):
        owner = "Graph/Node//Artifact//SSOT//Recorded//Event Record"
        scope = "MODEL//ANECHOIC <+ " + owner
        declaration = "from anechoic.formal_claims import declare_entity\n"
        claims = [
            (
                "record.md",
                scope,
                declaration + "class EventRecord:\n    pass\n"
                "declare_entity(entity_class=EventRecord, "
                "entity_name='Event Record', entity_kind='Primary')\n",
            ),
            (
                "id.md",
                scope + ".ID",
                declaration + f"declare_entity(entity_name='ID', "
                f"entity_kind='Property', base_path={owner!r}, "
                "relation_name='IS_PROPERTY_OF', value_format=str)\n",
            ),
            (
                "constraints.md",
                scope + ".Constraints",
                declaration + f"declare_entity(entity_name='Event Record "
                f"Constraints', constraints_for={owner!r}, "
                "population_unique_constraints=({'keys': ('ID',)},))\n",
            ),
            (
                "relation.md",
                "MODEL//ANECHOIC <+ Graph/Relation//IS_PROPERTY_OF",
                (
                    "from anechoic.formal_claims import declare_relation\n"
                    "declare_relation(relation_name='IS_PROPERTY_OF', "
                    "source_endpoint={}, target_endpoint={})\n"
                ),
            ),
        ]
        _check_relation_references(claims)
        with self.assertRaisesRegex(
            ValueError, "unknown population Property address"
        ):
            _check_relation_references([claims[0], *claims[2:]])

    def test_claim_language_descriptors_stay_outside_the_generated_model(self):
        language = carrier(
            "ANECHOIC_MODEL <+ CFEL", identifier="CA-R-2", body=""
        )
        operator = carrier(
            "ANECHOIC_MODEL <+ CFEL <+ Operator//Delivery",
            identifier="CA-R-3",
            body="",
        )
        self.assertEqual(
            select_model_claims([language, operator, carrier()]), (CLAIM,)
        )
        value_format = carrier(
            "ANECHOIC_MODEL <+ CFEL <+ Format", identifier="CA-R-4", body=""
        )
        with self.assertRaisesRegex(
            ValueError, "CA-R-4.md: expected one Formal Claim"
        ):
            select_model_claims([carrier(), value_format])

    def test_selects_model_and_ignores_structure_and_draft(self):
        model = carrier()
        structure = carrier(
            "ANECHOIC_STRUCTURE <+ Scope Unit//ENGINE",
            identifier="CA-R-2",
            body="",
        )
        draft = carrier(identifier="CA-R-3", status="draft", body="")
        self.assertEqual(
            select_model_claims([structure, draft, model]), (CLAIM,)
        )

    def test_duplicate_subject_and_identifier_fail_with_source(self):
        with self.assertRaisesRegex(
            ValueError, "CA-R-2.md: duplicate Declaration Subject"
        ):
            select_model_claims([carrier(), carrier(identifier="CA-R-2")])
        with self.assertRaisesRegex(
            ValueError, "CA-R-1.md: duplicate Current Declaration ID"
        ):
            select_model_claims([carrier(), carrier("ANECHOIC_MODEL <+ Node")])

    def test_mixed_missing_unclosed_and_non_native_claims_fail(self):
        formal = "## Claim\n### Formal Claim\n"
        bodies = (
            formal,
            formal + f"```python\n{CLAIM}```\n```CFEL\nNode\n```\n",
            formal + f"```python\n{CLAIM}",
            formal + "```python\nproperty_rule(address='Atom.Name')\n```\n",
        )
        for body in bodies:
            with (
                self.subTest(body=body),
                self.assertRaisesRegex(ValueError, "CA-R-1.md:"),
            ):
                select_model_claims([carrier(body=body)])

    def test_prose_example_is_not_a_formal_claim(self):
        body = f"## Claim\n### Prose Claim\n```python\n{CLAIM}```\n"
        with self.assertRaisesRegex(ValueError, "expected one Formal Claim"):
            select_model_claims([carrier(body=body)])

    def test_class_must_match_its_main_subject(self):
        claim = (
            "from anechoic.formal_claims import declare_entity\n"
            "class Atom:\n    pass\n"
            "declare_entity(entity_name='Atom', entity_class=Atom)\n"
        )
        body = f"## Claim\n### Formal Claim\n```python\n{claim}```\n"
        with self.assertRaisesRegex(
            ValueError, "declared class does not match its Main Subject"
        ):
            select_model_claims([carrier("ANECHOIC_MODEL <+ Node", body=body)])

    def test_rejects_ambiguous_sibling_order_before_generation(self):
        body = (
            "## Claim\n### Formal Claim\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Header', "
            "relation_name='IS_PROPERTY_OF', base_path='Atom', "
            "ordered_dependent_property_pairs=(('A', 'B'), ('C', 'D')))\n"
            "```\n"
        )
        with self.assertRaisesRegex(ValueError, "CA-R-1.md:.*disconnected"):
            select_model_claims(
                [carrier("ANECHOIC_MODEL <+ Atom.Header", body=body)]
            )

    def test_rejects_partial_dataclass_field_contract_before_generation(self):
        claim = (
            "from dataclasses import dataclass, field\n"
            "from anechoic.formal_claims import declare_entity\n"
            "@dataclass\nclass Example:\n"
            "    id: int = "
            "field(metadata={'property_occurrence_cardinality': 1, "
            "'value_cardinality': 1})\n"
            "declare_entity(entity_name='Example', entity_class=Example)\n"
        )

        def model(code):
            return carrier(
                "ANECHOIC_MODEL <+ Example",
                body=f"## Claim\n### Formal Claim\n```python\n{code}```\n",
            )

        self.assertEqual(select_model_claims([model(claim)]), (claim,))
        with self.assertRaisesRegex(
            ValueError, "require occurrence and value cardinalities"
        ):
            select_model_claims(
                [model(claim.replace("'value_cardinality': 1", "'other': 1"))]
            )
