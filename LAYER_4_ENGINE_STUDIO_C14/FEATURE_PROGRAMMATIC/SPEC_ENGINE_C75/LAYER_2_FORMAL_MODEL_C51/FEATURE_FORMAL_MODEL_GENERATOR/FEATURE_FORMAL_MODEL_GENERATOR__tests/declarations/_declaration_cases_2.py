import importlib

fixtures = importlib.import_module(
    "FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51."
    "FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__tests.declarations."
    "_declaration_fixtures"
)
CLAIM = fixtures.CLAIM
carrier = fixtures.carrier
endpoint_setup = fixtures.endpoint_setup
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


class DeclarationCases2:
    def test_qualified_class_property_short_path_resolves(self):
        root, workflow, content, relation, child = property_setup()
        self.assertEqual(
            len(select_model_claims([workflow, content, relation, child])), 4
        )
        with self.assertRaisesRegex(
            ValueError, "unknown Model address: Workflow.Content"
        ):
            select_model_claims([workflow, relation, child])

        def parsed(subject, args):
            return (
                "x",
                "ANECHOIC_MODEL <+ " + subject,
                {"kind": "entity", "arguments": args, "classes": ()},
            )

        kind = {"entity_name": "Workflow", "entity_class": "Workflow"}
        rows = [
            parsed(root, kind),
            parsed(root + ".Content", {}),
            parsed("Other/Workflow", kind),
            parsed("Other/Workflow.Content", {}),
        ]
        self.assertNotIn("Workflow.Content", _class_property_aliases(rows))

    def test_inherited_property_resolves_through_class_hierarchy(self):
        model, atom, ops, flow, prop, child, rel = inheritance_setup()
        self.assertEqual(
            len(select_model_claims([atom, ops, flow, prop, child, rel])), 6
        )
        full = model(
            "Workflow.Content.Claim",
            "CA-R-44",
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Claim', "
            "relation_name='IS_PROPERTY_OF', "
            "base_path='Atom/(.Header.Context.Role:=Operations)/"
            "Workflow.Content')",
        )
        self.assertEqual(
            len(select_model_claims([atom, ops, flow, prop, full, rel])), 6
        )
        with self.assertRaisesRegex(
            ValueError, "unknown Model address: Workflow.Content"
        ):
            select_model_claims([atom, ops, flow, child, rel])

        def row(subject, name=None, bases=()):
            args = {"entity_name": name, "entity_class": name} if name else {}
            classes = ({"name": name, "bases": bases},) if name else ()
            return (
                "x",
                "ANECHOIC_MODEL <+ " + subject,
                {"kind": "entity", "arguments": args, "classes": classes},
            )

        ambiguous = [
            row("A", "A"),
            row("B", "B"),
            row("C", "C", ("A", "B")),
            row("A.Content"),
            row("B.Content"),
        ]
        self.assertNotIn("C.Content", _class_property_aliases(ambiguous))
        ambiguous.append(row("C.Content"))
        self.assertNotIn("C.Content", _class_property_aliases(ambiguous))

    def test_qualified_endpoint_classes_are_checked(self):
        model, plan, step, rel = endpoint_setup()
        with self.assertRaisesRegex(ValueError, "CA-R-51.md:.*incompatible"):
            select_model_claims([step, plan, rel])
        inverse = model(
            "Relation//LINKS",
            "CA-R-52",
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='LINKS', "
            "source_endpoint={'level': 'instances', 'entity_paths': "
            "('Atom/(.Header.Context.Role := Operations)/Step',)}, "
            "target_endpoint={'level': 'instances', 'entity_paths': "
            "('Atom/(.Header.Context.Role := Plan)',)})",
        )
        self.assertEqual(len(select_model_claims([step, plan, inverse])), 3)

    def test_unparseable_subject_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "invalid Main Subject"):
            select_model_claims([carrier("ANECHOIC_MODEL <+")])

    def test_empty_model_is_an_error(self):
        structure = carrier(
            "ANECHOIC_STRUCTURE <+ Scope Unit//ENGINE", body=""
        )
        with self.assertRaisesRegex(
            ValueError, "No Current ANECHOIC_MODEL Declarations"
        ):
            select_model_claims([structure])
