"""Native contract graph test cases."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_support = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contract_graph_test_support"
)
compose_contract_graph = _graph.compose_contract_graph
render_contract_graph = _graph.render_contract_graph
extract_claim_constraints = _graph.extract_claim_constraints
compose_narrowing_graph = _graph.compose_narrowing_graph
build_subject_projection_data = _graph.build_subject_projection_data
carrier, body = _support.carrier, _support.body


class NativeContractCases2:
    def _native_property(
        self,
    ):
        step = "Atom/(.Header.Context.Role:=Operations)/Step"
        topic = "ANECHOIC_MODEL <+ Step.Kind"
        declarations = [
            carrier("CA-R-1", step, body()),
            carrier("CA-R-2", "Other/Step", body()),
            carrier(
                "CA-R-3",
                topic,
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_entity",
                    f"declare_entity(entity_name='Kind', "
                    f"relation_name='IS_PROPERTY_OF', base_path={step!r})",
                    "```",
                ),
            ),
        ]
        graph = compose_contract_graph(declarations)
        (node,) = [
            row for row in graph["entities"] if row["target"] == f"{step}.Kind"
        ]
        (entry,) = node["own"]
        self.assertEqual(topic, entry["subject"])
        self.assertEqual("CA-R-3", entry["source"]["atom_id"])
        self.assertEqual("native_property_base_path", entry["binding"])
        self.assertFalse(
            any(
                row["target"] in {"Step.Kind", "Other/Step.Kind"}
                for row in graph["entities"]
            )
        )

    locals()[
        (
            "test_native_property_uses_explicit_"
            "bearer_and_preserves_written_subject"
        )
    ] = _native_property

    def test_native_nested_bearers_resolve_independently_of_source_order(self):
        def property_declaration(atom_id, subject, base, name):
            return carrier(
                atom_id,
                subject,
                body(
                    "### Formal Claim",
                    "```python",
                    "from anechoic.formal_claims import declare_entity",
                    f"declare_entity(entity_name={name!r}, "
                    f"relation_name='IS_PROPERTY_OF', base_path={base!r})",
                    "```",
                ),
            )

        declarations = [
            carrier("CA-R-1", "Atom", body()),
            property_declaration("CA-R-2", "Short.Header", "Atom", "Header"),
            property_declaration(
                "CA-R-3", "Header.Context", "Atom.Header", "Context"
            ),
            property_declaration(
                "CA-R-4", "Context.Role", "Atom.Header.Context", "Role"
            ),
        ]
        for rows in (declarations, list(reversed(declarations))):
            graph = compose_contract_graph(rows)
            targets = {
                entry["source"]["atom_id"]: node["target"]
                for node in graph["entities"]
                for entry in node["own"]
            }
            self.assertEqual("Atom.Header.Context.Role", targets["CA-R-4"])

    def test_native_python_class_inheritance_and_relation_metadata(self):
        root = carrier("CA-R-1", "Atom", body())
        method = carrier(
            "CA-R-2",
            "Atom/(.Header.Context.Role := Method)",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_entity",
                "from anechoic.model import Atom",
                "class Method(Atom):",
                "    pass",
                (
                    "declare_entity(entity_class=Method, enti"
                    "ty_name='Method', qualification_property"
                    "_path='Atom.Header.Context.Role')"
                ),
                "```",
            ),
        )
        tree, _ = compose_narrowing_graph([root, method])
        identities = {node["id"]: node["identity"] for node in tree["nodes"]}
        self.assertIn(
            ("Atom/(.Header.Context.Role:=Method)", "Atom"),
            {
                (
                    identities[edge["relation_source"]],
                    identities[edge["relation_target"]],
                )
                for edge in tree["edges"]
            },
        )
        self.check_relation_metadata()

    def check_relation_metadata(self):
        relation = carrier(
            "CA-R-3",
            "Relation//CARRIES",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_relation",
                (
                    "declare_relation(relation_name='CARRIES'"
                    ", source_endpoint={'level': 'instances',"
                    " 'entity_paths': ('Carrier',)}, target_e"
                    "ndpoint={'level': 'instances'}, inverse_"
                    "alias='IS_CARRIED_BY', written_alias='>>"
                    "')"
                ),
                "```",
            ),
        )
        clauses, diagnostics = extract_claim_constraints(relation)
        self.assertEqual([], diagnostics)
        self.assertEqual(
            2, sum(row["kind"] == "relation_endpoint" for row in clauses)
        )
        self.assertTrue(
            any(row.get("relation") == "HAS_INVERSE" for row in clauses)
        )
        self.assertTrue(any(row.get("glyph") == ">>" for row in clauses))

    def test_native_direct_relation_preserves_the_legacy_inverse_view(self):
        direct, inverse = self.direct_relation_carriers()
        graph = compose_contract_graph([direct, inverse])
        view = next(
            row["derived_view"]
            for row in graph["relations"]
            if row["target"] == "IS_CARRIED_BY"
        )
        (endpoint,) = view["endpoints"]
        self.assertEqual(
            {"level": "instances", "ephemeral": False}, endpoint["host"]
        )
        self.assertEqual(("Carrier",), endpoint["target"]["entity_paths"])
        self.assertEqual(
            {"minimum": 1, "maximum": 1}, endpoint["sources_per_target"]
        )
        self.assertEqual([], graph["missing_relation_semantics"])
        self.assertEqual([], graph["inheritance_diagnostics"])
        direct_row = next(
            row for row in graph["relations"] if row["target"] == "CARRIES"
        )
        self.assertNotIn("derived_aliases", direct_row)

    def direct_relation_carriers(self):
        direct = carrier(
            "CA-R-1",
            "Relation//CARRIES",
            body(
                "### Formal Claim",
                "```python",
                "from anechoic.formal_claims import declare_relation",
                (
                    "declare_relation(relation_name='CARRIES'"
                    ", source_endpoint={'level': 'instances',"
                    " 'entity_paths': ('Carrier',)},"
                ),
                (
                    "                 target_endpoint={'level"
                    "': 'instances', 'ephemeral': False},"
                ),
                (
                    "                 inverse_alias='IS_CARRI"
                    "ED_BY', targets_per_source=1)"
                ),
                "```",
                "### Prose Claim",
                "The Carrier represents the object.",
            ),
        )
        inverse = carrier(
            "CA-R-2",
            "Relation//IS_CARRIED_BY",
            body(
                "### Formal Claim",
                "```python",
                (
                    "relation(source='Relation//IS_CARRIED_BY"
                    "', name='HAS_INVERSE', target='Relation/"
                    "/CARRIES', reverse=True)"
                ),
                "```",
            ),
        )
        return direct, inverse

    def _native_inverse(
        self,
    ):
        direct = self.inverse_declaration()
        graph = compose_contract_graph([direct])
        self.assertEqual(
            ["CARRIES"], [row["target"] for row in graph["relations"]]
        )
        direct_row = graph["relations"][0]
        (alias,) = direct_row["derived_aliases"]
        self.assertEqual(
            ("IS_CARRIED_BY", "Derived", "CARRIES"),
            (alias["name"], alias["classification"], alias["direct_relation"]),
        )
        self.assertEqual("CA-R-1", alias["source"]["atom_id"])
        (endpoint,) = alias["endpoints"]
        self.assertEqual(("Atom",), endpoint["host"]["entity_paths"])
        self.assertEqual(("Carrier",), endpoint["target"]["entity_paths"])
        self.assertEqual(
            {"minimum": 1, "maximum": 5}, endpoint["targets_per_source"]
        )
        self.assertEqual(
            {"minimum": 2, "maximum": 3}, endpoint["sources_per_target"]
        )
        self.assertEqual(2, len(direct_row["host_target"]))
        self.assertIn(
            "Derived Relation `((IS_CARRIED_BY))`",
            render_contract_graph(graph),
        )

    def inverse_declaration(self):
        return carrier(
            "CA-R-1",
            "Relation//CARRIES",
            body(
                "### Formal Claim",
                "```python",
                (
                    "from anechoic.formal_claims import Cardi"
                    "nality, declare_relation"
                ),
                "declare_relation(relation_name='CARRIES',",
                (
                    "  source_endpoint={'level': 'instances',"
                    " 'entity_paths': ('Carrier',)},"
                ),
                (
                    "  target_endpoint={'level': 'instances',"
                    " 'entity_paths': ('Atom',)},"
                ),
                "  inverse_alias='IS_CARRIED_BY',",
                "  targets_per_source=Cardinality(minimum=2, maximum=3),",
                "  sources_per_target=Cardinality(minimum=1, maximum=5))",
                "```",
                semantics="The Carrier represents the object.",
            ),
        )

    locals()[
        (
            "test_native_inverse_without_separate"
            "_declaration_keeps_source_and_bounds"
        )
    ] = _native_inverse
