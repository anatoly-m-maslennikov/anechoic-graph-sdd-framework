"""Direct and scoped contract relation cases."""

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
build_subject_projection_data = _graph.build_subject_projection_data
carrier, body = _support.carrier, _support.body


def unary_carriers():
    return [
        carrier(
            "CA-R-1",
            "Node",
            body(
                "```python",
                "# model",
                (
                    "relation(source='(Node, Node.**)', name="
                    "'IS_DECLARED_BY', source_count='1')"
                ),
                "```",
            ),
        ),
        carrier(
            "CA-R-2",
            "Atom",
            body(
                "```python",
                "# instances",
                (
                    "relation(source='Atom//$atom', name='HAS"
                    "_ACTIVE_SUBJECT', source_count='0..1')"
                ),
                (
                    "relation(source='Atom//$atom', name='GOV"
                    "ERNS', source_count='0..1')"
                ),
                "```",
            ),
        ),
    ]


class ContractRelationCases2:
    def test_python_order_claim_preserves_graph_relation(self):
        python = carrier(
            "CA-R-1",
            "Atom",
            body(
                "```python",
                "# model",
                'order_before(first="Atom.A", second="Atom.B")',
                "```",
            ),
        )
        clauses, diagnostics = extract_claim_constraints(python)
        self.assertEqual([], diagnostics)
        self.assertEqual("IS_ORDERED_RIGHT_BEFORE", clauses[0]["relation"])
        self.assertEqual(
            ("Atom.A", "Atom.B"),
            (clauses[0]["source_selector"], clauses[0]["target_selector"]),
        )

    def test_operator_symbol_is_bound_to_its_declared_subject(self):
        address = "ANECHOIC_MODEL <+ CFEL <+ Operator//Delivery"
        python = carrier(
            "CA-R-1",
            address,
            body(
                "### Formal Claim",
                "```python",
                "# model",
                "set_value(address='Operator//Delivery', value='\">>\"')",
                "```",
            ),
        )
        clauses, diagnostics = extract_claim_constraints(python)
        self.assertFalse(diagnostics)
        self.assertEqual(
            [(row["kind"], row["operator"], row["symbol"]) for row in clauses],
            [("operator_symbol", "Delivery", ">>")],
        )
        python["subjects"]["active"] = address.replace("Delivery", "Alias")
        records, issues = extract_claim_constraints(python)
        self.assertFalse(records)
        self.assertEqual(len(issues), 1)
        python["subjects"]["active"] = address
        python["body"] = body(
            "### Formal Claim",
            "```python",
            "# model",
            r"""set_value(address="Operator//Delivery", value='"\\q"')""",
            "```",
        )
        records, issues = extract_claim_constraints(python)
        self.assertFalse(records)
        self.assertEqual(len(issues), 1)

    def test_unary_relation_counts_keep_source_scope_and_no_target(self):
        graph = compose_contract_graph(unary_carriers())
        node = next(
            row for row in graph["entities"] if row["target"] == "Node"
        )
        atom = next(
            row for row in graph["entities"] if row["target"] == "Atom"
        )
        clauses = (
            node["own"][0]["clauses"] + atom["own"][0]["instance_clauses"]
        )
        self.assertEqual(
            ["IS_DECLARED_BY", "HAS_ACTIVE_SUBJECT", "GOVERNS"],
            [row["relation"] for row in clauses],
        )
        self.assertEqual(
            ["model", "instances", "instances"],
            [row["group"] for row in clauses],
        )
        self.assertEqual(
            ["(Node, Node.**)", "Atom//$atom", "Atom//$atom"],
            [row["source_selector"] for row in clauses],
        )
        self.assertEqual(
            [
                {"minimum": 1, "maximum": 1},
                {"minimum": 0, "maximum": 1},
                {"minimum": 0, "maximum": 1},
            ],
            [row["source_cardinality"] for row in clauses],
        )
        self.assertTrue(
            all(
                row["target_selector"] is None
                and row["target_domain"] == "unresolved"
                and row["written_direction"] == "forward"
                for row in clauses
            )
        )
        self.assertEqual([], graph["relations"])
        self.assertEqual(
            {"Node", "Atom"}, {row["target"] for row in graph["entities"]}
        )
        self.check_unary_rendering(graph)

    def check_unary_rendering(self, graph):
        document = render_contract_graph(graph)
        self.assertIn(
            (
                "`(Node, Node.**)` — IS_DECLARED_BY; outg"
                "oing count=1; target domain unresolved"
            ),
            document,
        )
        self.assertIn(
            (
                "`Atom//$atom` — HAS_ACTIVE_SUBJECT; outg"
                "oing count=0..1; target domain unresolve"
                "d"
            ),
            document,
        )
        self.assertIn(
            (
                "`Atom//$atom` — GOVERNS; outgoing count="
                "0..1; target domain unresolved"
            ),
            document,
        )
        self.assertNotIn("→ `None`", document)
