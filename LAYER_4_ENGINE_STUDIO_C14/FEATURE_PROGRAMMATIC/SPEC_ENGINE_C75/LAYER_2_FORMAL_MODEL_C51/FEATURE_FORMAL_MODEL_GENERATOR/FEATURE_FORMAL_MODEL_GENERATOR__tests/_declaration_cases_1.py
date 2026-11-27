import importlib

fixtures = importlib.import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests."
    "_declaration_fixtures"
)
CLAIM = fixtures.CLAIM
carrier = fixtures.carrier
inverse_setup = fixtures.inverse_setup
endpoint_relation_setup = fixtures.endpoint_relation_setup
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


class DeclarationCases1:
    def test_relation_endpoints_and_entity_relation_must_be_declared(self):
        with_claim, relation, entity, atom, node, link = (
            endpoint_relation_setup()
        )
        self.assertEqual(len(select_model_claims([atom, node, link])), 3)
        with self.assertRaisesRegex(ValueError, "unknown Relation: LINKS"):
            select_model_claims([atom, node])
        with self.assertRaisesRegex(ValueError, "unknown Model address: Node"):
            select_model_claims([atom, link])
        unknown_entity = with_claim(
            "ANECHOIC_MODEL <+ Node",
            "CA-R-5",
            entity.replace("LINKS", "MISSING"),
        )
        with self.assertRaisesRegex(
            ValueError, "CA-R-3.md:.*unknown Model address: Atom"
        ):
            select_model_claims([unknown_entity, link])
        mismatch = with_claim(
            "ANECHOIC_MODEL <+ Relation//OTHER", "CA-R-4", relation
        )
        with self.assertRaisesRegex(
            ValueError, "Relation does not match its Main Subject"
        ):
            select_model_claims([atom, node, mismatch])

    def test_derived_inverse_can_be_referenced_without_a_second_declaration(
        self,
    ):
        relation = (
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', "
            "inverse_alias='LINKED_BY', "
            "source_endpoint={'level': 'instances'}, "
            "target_endpoint={'level': 'instances'})"
        )
        entity = (
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Atom', instance_relation_constraints="
            "{'LINKED_BY': {'target_entity_paths': ('Atom',)}})"
        )

        def body(claim):
            return f"## Claim\n### Formal Claim\n```python\n{claim}\n```\n"

        atom = carrier(body=body(entity))
        link = carrier(
            "ANECHOIC_MODEL <+ Relation//LINKS",
            identifier="CA-R-2",
            body=body(relation),
        )
        self.assertEqual(len(select_model_claims([atom, link])), 2)

    def test_relation_constraints_check_levels_inheritance_inverse_and_pairs(
        self,
    ):
        model, entity, animal, cat, food, toy, link = relation_setup()
        select_model_claims([animal, cat, food, toy, link])
        inverse = inverse_setup(model, entity)
        select_model_claims([animal, cat, inverse, toy, link])
        wrong_pair = model(
            "Cat",
            "CA-R-11",
            entity(
                "Cat",
                "(Animal)",
                ", instance_relation_constraints={'EATS': "
                "{'target_entity_paths': ('Toy',)}}",
            ),
        )
        with self.assertRaisesRegex(ValueError, "CA-R-11.md:.*incompatible"):
            select_model_claims([animal, wrong_pair, food, toy, link])
        wrong_level = model(
            "Cat",
            "CA-R-11",
            entity(
                "Cat", "(Animal)", ", model_relation_constraints={'EATS': {}}"
            ),
        )
        with self.assertRaisesRegex(ValueError, "CA-R-11.md:.*incompatible"):
            select_model_claims([animal, wrong_level, food, toy, link])
        prohibition = model(
            "Cat",
            "CA-R-11",
            entity(
                "Cat",
                "(Animal)",
                ", model_relation_constraints={'EATS': "
                "{'targets_per_source': 0}}",
            ),
        )
        select_model_claims([animal, prohibition, food, toy, link])

    def test_cfel_wrapped_entity_is_available_by_its_local_name(self):
        relation_entity = carrier(
            "ANECHOIC_MODEL <+ CFEL <+ Relation",
            body=(
                "## Claim\n### Formal Claim\n```python\n"
                "from anechoic.formal_claims import declare_entity\n"
                "declare_entity(entity_name='Relation')\n```\n"
            ),
        )
        link = carrier(
            "ANECHOIC_MODEL <+ CFEL <+ Relation//LINKS",
            identifier="CA-R-2",
            body=(
                "## Claim\n### Formal Claim\n```python\n"
                "from anechoic.formal_claims import declare_relation\n"
                "declare_relation(relation_name='LINKS', "
                "source_endpoint={'entity_paths': ('Relation',)}, "
                "target_endpoint={'entity_paths': ('Relation',)})\n```\n"
            ),
        )
        self.assertEqual(len(select_model_claims([relation_entity, link])), 2)

    def test_relation_catalog_accepts_exact_legacy_and_graph_scopes(self):
        declaration = {
            "kind": "relation",
            "arguments": {
                "relation_name": "LINKS",
                "inverse_alias": "LINKED_BY",
            },
        }
        for path in ("Relation//LINKS", "Graph/Relation//LINKS"):
            with self.subTest(path=path):
                catalog = build_relation_declaration_catalog(
                    [("source", "MODEL//ANECHOIC <+ " + path, declaration)]
                )
                self.assertEqual(set(catalog), {"LINKS", "LINKED_BY"})
                self.assertTrue(catalog["LINKED_BY"][1])
        for subject in (
            "MODEL//ANECHOIC <+ Graph/Relation//OTHER",
            "MODEL//ANECHOIC <+ Graph//Relation//LINKS",
            "MODEL//ANECHOIC <+ Other/Relation//LINKS",
            "Graph/Relation//LINKS",
        ):
            with (
                self.subTest(subject=subject),
                self.assertRaisesRegex(ValueError, "does not match"),
            ):
                build_relation_declaration_catalog(
                    [("source", subject, declaration)]
                )

    def test_relation_registry_resolves_derived_names_after_assembly(self):
        def relation(name, **args):
            return (
                name + ".md",
                "ANECHOIC_MODEL <+ CFEL <+ Relation//" + name,
                {
                    "kind": "relation",
                    "arguments": {"relation_name": name, **args},
                },
            )

        base = relation("BASE", inverse_alias="REVERSE")
        derived = relation("DERIVED", derived_from="REVERSE")
        registry = build_relation_declaration_catalog([derived, base])
        self.assertEqual(set(registry), {"BASE", "REVERSE", "DERIVED"})
        self.assertTrue(registry["REVERSE"][1])
        with self.assertRaisesRegex(
            ValueError, "unknown derived_from Relation"
        ):
            build_relation_declaration_catalog(
                [relation("DERIVED", derived_from="MISSING")]
            )
        with self.assertRaisesRegex(ValueError, "cannot derive from itself"):
            build_relation_declaration_catalog(
                [
                    relation(
                        "DERIVED", inverse_alias="ALIAS", derived_from="ALIAS"
                    )
                ]
            )
        with self.assertRaisesRegex(ValueError, "duplicate Relation name"):
            build_relation_declaration_catalog(
                [base, relation("OTHER", inverse_alias="REVERSE")]
            )

        native = registry_native

        first = native("DERIVED", ", derived_from='REVERSE'", "CA-R-20")
        second = native("BASE", ", inverse_alias='REVERSE'", "CA-R-21")
        self.assertEqual(len(select_model_claims([first, second])), 2)
        with self.assertRaisesRegex(
            ValueError, "unknown derived_from Relation"
        ):
            select_model_claims([first])
