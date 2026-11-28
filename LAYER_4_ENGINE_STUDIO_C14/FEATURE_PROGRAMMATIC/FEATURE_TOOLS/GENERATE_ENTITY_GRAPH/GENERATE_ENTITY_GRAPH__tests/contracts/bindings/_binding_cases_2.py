"""Source-bound contract graph cases."""

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
carrier, body = _support.carrier, _support.body
scope_context_graph = _support.scope_context_graph
_sources = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.contracts.bindings._binding_sources"
)


class BindingCases2:
    def _case_187(
        self,
    ):
        graph = compose_contract_graph(
            _sources.carriers_3_1()
            + _sources.carriers_3_2()
            + _sources.carriers_3_3()
        )

        rows = {row["target"]: row for row in graph["entities"]}
        self.assertEqual(
            "allowed_value_condition",
            rows["Atom.Status"]["shared"][0]["binding"],
        )
        self.assertEqual(
            "Atom.Status:Draft", rows["Atom.Status"]["shared"][0]["subject"]
        )
        self.assertEqual(
            "property_qualification",
            rows["Projection"]["shared"][0]["binding"],
        )
        self.assertNotIn("Projection/(.Form:=ApplicableMethodology)", rows)
        self.assertEqual(1, graph["coverage"]["coverage_gaps"])
        self.assertEqual(1, graph["coverage"]["outside_model_scope_sources"])
        self.assertEqual(
            "outside_model_scope",
            graph["outside_model_scope"][0]["selection_disposition"],
        )

    locals()[
        (
            "test_binds_only_declared_value_and_qualifie"
            "r_conditions_and_keeps_other_evidence_scoped"
        )
    ] = _case_187

    def test_namespace_declaration_preserves_claim_without_creating_node(self):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "ANECHOIC_MODEL",
                    body(
                        "```python",
                        (
                            "classify(address='MODEL', axis='Containe"
                            "r', value='yes', notation='relation')"
                        ),
                        "```",
                    ),
                ),
                carrier("CA-R-2", "UNKNOWN_MODEL", body("Unknown.")),
            ]
        )
        self.assertEqual(
            ["ANECHOIC_MODEL"], [row["target"] for row in graph["namespaces"]]
        )
        self.assertEqual(
            ["UNKNOWN_MODEL"], [row["target"] for row in graph["entities"]]
        )
        self.assertEqual([], graph["coverage_gaps"])
        self.assertIn(
            "`MODEL` — HAS_AXIS → `Container == yes`",
            render_contract_graph(graph),
        )

    def test_render_written_and_effective_occurrence_and_value_bounds(self):
        graph = compose_contract_graph(
            [
                carrier("CA-R-1", "Node", body("Node.")),
                carrier(
                    "CA-R-2",
                    "Node.Name",
                    body(
                        "```python",
                        (
                            "from anechoic.formal_claims import decla"
                            "re_entity, Cardinality"
                        ),
                        (
                            "declare_entity(entity_name='Name', relat"
                            "ion_name='IS_PROPERTY_OF', base_path='No"
                            "de', property_occurrence_cardinality=Car"
                            "dinality(minimum=0, maximum=1), value_fo"
                            "rmat='string', value_cardinality=Cardina"
                            "lity(minimum=0, maximum=1))"
                        ),
                        "```",
                    ),
                ),
            ]
        )
        document = render_contract_graph(graph)
        self.assertIn(
            "written names count=0..1; effective names count=0..1", document
        )
        self.assertIn("values count=0..1", document)

    def test_binds_only_source_proven_scope_unit_declaration_instance_contexts(
        self,
    ):
        graph = scope_context_graph()

        entities = {row["target"]: row for row in graph["entities"]}
        scope_shared = entities["Scope Unit"]["shared"]
        project_shared = entities["Project"]["shared"]
        projection_shared = entities["Projection"]["shared"]
        selection_shared = entities["Named Selection"]["shared"]
        structure_shared = entities["PROJECT STRUCTURE"]["shared"]
        self.assertEqual(
            ["CA-R-3@1", "CA-R-5@1"], entities["Scope Unit"]["shared_sources"]
        )
        self.assertEqual(
            "scope_unit_declaration_context", scope_shared[0]["binding"]
        )
        self.assertEqual(
            "scope_unit_declaration_context", project_shared[0]["binding"]
        )
        self.assertEqual(
            "current_scope_unit_declaration",
            scope_shared[0]["binding_context"]["existence_provenance"],
        )
        self.assertEqual(
            {"atom_id": "CA-R-3", "version": 1, "path": "sources/CA-R-3.md"},
            scope_shared[1]["binding_context"]["declaration_source"],
        )
        self.assertEqual(
            "CA-R-4",
            project_shared[1]["binding_context"]["declaration_source"][
                "atom_id"
            ],
        )
        self.check_scope_contexts(
            graph,
            entities,
            projection_shared,
            selection_shared,
            structure_shared,
        )

    def check_scope_contexts(
        self,
        graph,
        entities,
        projection_shared,
        selection_shared,
        structure_shared,
    ):
        self.assertEqual(
            "known_instance_context", projection_shared[0]["binding"]
        )
        self.assertEqual(
            "known_instance_context", selection_shared[0]["binding"]
        )
        self.assertEqual(
            "known_instance_context", structure_shared[0]["binding"]
        )
        self.assertEqual(
            "bounded_named_contract_context",
            selection_shared[0]["binding_context"]["existence_provenance"],
        )
        self.assertEqual(
            ["CA-R-1"],
            [
                row["source"]["atom_id"]
                for row in entities["Scope Unit"]["own"]
            ],
        )
        self.assertNotIn("Scope Unit//CORE_META_MODEL", entities)
        self.assertNotIn("Actor//ANATOLY", entities)
        self.assertEqual(2, graph["coverage"]["coverage_gaps"])
        self.assertEqual(2, graph["coverage"]["outside_model_scope_sources"])
        self.assertEqual(
            {"CA-R-7", "CA-R-15"},
            {row["source"]["atom_id"] for row in graph["coverage_gaps"]},
        )
        self.assertEqual(
            {"CA-R-8", "CA-R-14"},
            {row["source"]["atom_id"] for row in graph["outside_model_scope"]},
        )
