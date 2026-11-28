"""Native contract graph test cases."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.contracts__shared"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
extract_claim_constraints = _graph.extract_claim_constraints
compose_narrowing_graph = _graph.compose_narrowing_graph
build_subject_projection_data = _graph.build_subject_projection_data
carrier, body = _support.carrier, _support.body


class NativeContractCases3:
    def test_native_dependent_counts(self):
        address = "Atom.Header.Relations"
        native = self.dependent_claim()

        self.assertEqual(
            {
                "property": (
                    None,
                    {"minimum": 0, "maximum": 1},
                    None,
                    {"minimum": 0, "maximum": 0},
                ),
                "immediate_dependents": (
                    "string",
                    {"minimum": 1, "maximum": None},
                    None,
                    None,
                ),
                "immediate_dependent_values": (
                    None,
                    None,
                    "string",
                    {"minimum": 1, "maximum": None},
                ),
            },
            self.counts_contracts(address, native),
        )

    def dependent_claim(self):
        return body(
            "### Formal Claim",
            "```python",
            "from anechoic.formal_claims import declare_entity",
            "from anechoic.formal_claims import Cardinality",
            (
                "declare_entity(entity_name='Relations', "
                "relation_name='IS_PROPERTY_OF', base_pat"
                "h='Atom.Header',"
            ),
            (
                "  property_occurrence_cardinality=Cardin"
                "ality(minimum=0, maximum=1), value_cardi"
                "nality=0,"
            ),
            (
                "  dependent_property_cardinality=Cardina"
                "lity(minimum=1, maximum=None), dependent"
                "_property_name_format=str,"
            ),
            "  dependent_property_value_format=str,",
            (
                "  dependent_property_value_cardinality=C"
                "ardinality(minimum=1, maximum=None))"
            ),
            "```",
        )

    def counts_contracts(self, address, claim):
        atom = carrier("CA-R-1", address, claim)
        graph = compose_contract_graph([atom])
        (entry,) = next(
            row for row in graph["entities"] if row["target"] == address
        )["own"]
        self.assertFalse(entry["diagnostics"])

        def format_name(value):
            return "string" if value == "str" else value or None

        return {
            clause["selection"]: (
                format_name(clause.get("name_format")),
                clause.get("occurrence_cardinality"),
                format_name(clause.get("value_format")),
                clause.get("value_cardinality"),
            )
            for clause in entry["clauses"]
            if clause["kind"] == "property_constraint"
        }

    def test_native_order_keeps_property_scope_and_source(self):
        atom = carrier("CA-R-1", "Atom", body())
        claim = self.order_claim()
        graph = compose_contract_graph([atom, claim])
        prop = next(
            node
            for node in graph["entities"]
            if node["target"] == "Atom.Content.Claim"
        )
        (order,) = [
            clause
            for clause in prop["own"][0]["clauses"]
            if clause.get("relation") == "IS_ORDERED_RIGHT_BEFORE"
        ]
        self.assertEqual("relation_cardinality", order["kind"])
        self.assertEqual("Atom.Content.Claim", order["bearer"])
        self.assertEqual(
            (
                "Atom.Content.Claim.Prose Claim",
                "Atom.Content.Claim.Formal Claim",
            ),
            (order["source_selector"], order["target_selector"]),
        )
        self.assertEqual(
            ("Requirement", "Method", "Evaluation", "Delivery"),
            order["applicable_entity_classes"],
        )
        self.assertEqual("CA-R-2", order["source"]["atom_id"])
        self.check_order_projection(atom, claim, order)

    def order_claim(self):
        return carrier(
            "CA-R-2",
            "Atom.Content.Claim",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_entity",
                (
                    "from anechoic.model import Requirement, "
                    "Method, Evaluation, Delivery"
                ),
                (
                    "declare_entity(entity_name='Claim', rela"
                    "tion_name='IS_PROPERTY_OF', base_path='A"
                    "tom.Content',"
                ),
                (
                    "  dependent_property_cardinality=2, allo"
                    "wed_dependent_property_names=('Prose Cla"
                    "im', 'Formal Claim'),"
                ),
                (
                    "  ordered_dependent_property_pairs=(('Pr"
                    "ose Claim', 'Formal Claim'),),"
                ),
                (
                    "  applies_to_entity_classes=(Requirement"
                    ", Method, Evaluation, Delivery))"
                ),
                "```",
            ),
        )

    def check_order_projection(self, atom, claim, order):
        role = carrier(
            "CA-R-3",
            "Atom/(.Header.Context.Role:=Requirement)",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_entity",
                "from anechoic.model import Atom",
                "class Requirement(Atom):",
                "    pass",
                (
                    "declare_entity(entity_class=Requirement,"
                    " entity_name='Requirement', qualificatio"
                    "n_property_path='Atom.Header.Context.Rol"
                    "e')"
                ),
                "```",
            ),
        )
        projection = build_subject_projection_data([atom, claim, role])
        base = next(
            row for row in projection["entities"] if row["identity"] == "Atom"
        )
        self.assertNotIn(
            "Atom.Content.Claim",
            [row["identity"] for row in base["direct_properties"]],
        )
        entity = next(
            row
            for row in projection["entities"]
            if row["identity"] == "Atom/(.Header.Context.Role:=Requirement)"
        )
        projected = next(
            row
            for row in entity["inherited_properties"]
            if row["identity"] == "Atom.Content.Claim"
        )
        self.assertIn(order, projected["contracts"])
