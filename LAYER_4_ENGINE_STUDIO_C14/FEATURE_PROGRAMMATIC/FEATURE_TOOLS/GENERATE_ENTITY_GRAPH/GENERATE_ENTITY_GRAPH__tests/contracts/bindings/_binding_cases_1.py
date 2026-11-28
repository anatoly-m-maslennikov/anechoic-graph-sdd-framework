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


class BindingCases1:
    def test_explicit_namespace_header_qualifications_bind_declared_properties(
        self,
    ):
        graph = compose_contract_graph(
            _sources.carriers_1_1()
            + _sources.carriers_1_2()
            + _sources.carriers_1_3()
            + _sources.carriers_1_4()
        )
        rows = {row["target"]: row for row in graph["entities"]}
        self.assertEqual(
            {
                "Atom",
                "Atom.Header",
                "Atom.Header.Role",
                "Atom.Header.Form",
                "Atom.Content.Claim",
                "Node",
            },
            set(rows),
        )
        self.assertEqual(
            {"Atom.Header.Role", "Atom.Header.Form"},
            {
                row["binding_context"]["property"]
                for row in rows["Atom"]["shared"]
                if "property" in row["binding_context"]
            },
        )
        combined = next(
            row
            for row in rows["Atom"]["shared"]
            if row["source"]["atom_id"] == "CA-R-9"
        )
        self.assertEqual(
            ["Atom.Header.Role", "Atom.Header.Form"],
            combined["binding_context"]["properties"],
        )
        self.assertEqual(
            "CA-R-12",
            rows["Atom.Content.Claim"]["shared"][0]["source"]["atom_id"],
        )
        self.assertEqual([], rows["Node"]["shared"])
        self.check_complex_scope(graph)

    def check_complex_scope(self, graph):
        self.assertIn(
            "complex selection scope", graph["coverage_gaps"][0]["message"]
        )

    def _case_68(
        self,
    ):
        graph = compose_contract_graph(
            _sources.carriers_2_1()
            + _sources.carriers_2_2()
            + _sources.carriers_2_3()
        )

        rows = {row["target"]: row for row in graph["entities"]}
        child = rows["Node/Parent/Child"]
        self.assertEqual(["CA-D-6@1", "CA-R-5@1"], child["shared_sources"])
        self.assertEqual(
            ["Node/Parent", "Node"],
            [row["target"] for row in child["transitive_ancestors"]],
        )
        self.assertEqual(
            ["Node/Parent.Status"],
            [
                row["target"]
                for row in child["inherited_property_declarations"]
            ],
        )
        self.assertNotIn("Node/Parent/Child.Status", rows)
        self.assertEqual(1, graph["coverage"]["coverage_gaps"])
        self.assertIn(
            "Node/Unknown.Status",
            graph["coverage_gaps"][0]["blocks"][0]["block"],
        )
        rendered = render_contract_graph(graph)
        self.assertLess(
            rendered.index("## Declared Narrowing Tree"),
            rendered.index("## Entity and Property Contracts"),
        )
        self.assertIn("Transitive ancestor Declarations", rendered)
        self.assertIn("Inherited Property Declaration refs", rendered)

    locals()[
        (
            "test_attaches_exact_shared_rmed_evidence_an"
            "d_links_transitive_properties_without_copies"
        )
    ] = _case_68

    def test_keeps_cfel_component_and_semantics_without_inventing_a_node(self):
        graph = compose_contract_graph(
            [
                carrier(
                    "CA-R-1",
                    "CFEL <+ Format",
                    body("Format declaration.", semantics="A CFEL component."),
                ),
                carrier("CA-R-2", "CFEL", body("CFEL root declaration.")),
                carrier(
                    "CA-R-3", "Operator", body("Operator kind declaration.")
                ),
                carrier(
                    "CA-R-4",
                    "Operator//Anatoly",
                    body("Operator instance declaration."),
                ),
            ]
        )

        self.assertEqual(
            ["CFEL", "Format"], [row["target"] for row in graph["components"]]
        )
        self.assertEqual(
            {("Operator", "primary_node"), ("Operator//Anatoly", "instance")},
            {(row["target"], row["kind"]) for row in graph["entities"]},
        )
        instance = next(
            row for row in graph["entities"] if row["kind"] == "instance"
        )
        self.assertEqual(
            ["CA-R-3@1"], instance["instance_of"]["effective_source_refs"]
        )
        rendered = render_contract_graph(graph)
        self.assertIn("CFEL, Carrier, and Term Component Contracts", rendered)
        self.assertIn("A CFEL component.", rendered)

    def _case_140(
        self,
    ):
        graph = compose_contract_graph(
            [
                carrier("CA-R-1", "CFEL", body("CFEL root declaration.")),
                carrier(
                    "CA-R-2", "CFEL <+ Format", body("Format declaration.")
                ),
                carrier(
                    "CA-R-3",
                    "CFEL <+ Format.Data Type",
                    body("Format Property declaration."),
                ),
                carrier(
                    "CA-R-4",
                    "CFEL <+ Format//markdown",
                    body("Markdown format declaration."),
                ),
                carrier(
                    "CA-R-5", "CFEL <+ Operator", body("Operator declaration.")
                ),
                carrier(
                    "CA-R-6",
                    "CFEL <+ Operator//Addition",
                    body("Addition declaration."),
                ),
            ]
        )

        rows = {row["target"]: row for row in graph["entities"]}
        self.assertEqual("property", rows["Format.Data Type"]["kind"])
        self.assertEqual("instance", rows["Format//markdown"]["kind"])
        self.assertEqual("instance", rows["Operator//Addition"]["kind"])
        self.assertEqual(
            ["CA-R-2@1"],
            rows["Format//markdown"]["instance_of"]["effective_source_refs"],
        )
        self.assertEqual(
            {"CFEL", "Format", "Operator"},
            {row["identity"] for row in graph["narrowing_tree"]["nodes"]},
        )
        self.assertEqual([], graph["narrowing_tree"]["edges"])
        self.assertFalse(graph["inheritance_diagnostics"])
        self.assertEqual(0, graph["coverage"]["coverage_gaps"])
        self.assertEqual(0, graph["coverage"]["instance_kind_gaps"])

    locals()[
        (
            "test_keeps_explicit_cfel_component_prope"
            "rties_and_instances_out_of_narrowing_tree"
        )
    ] = _case_140
