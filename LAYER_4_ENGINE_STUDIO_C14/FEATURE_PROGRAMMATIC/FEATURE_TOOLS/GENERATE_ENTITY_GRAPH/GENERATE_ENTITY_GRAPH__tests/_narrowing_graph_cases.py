"""Declared path and reference edge case."""

from importlib import import_module

_graph = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__shared"
)
_fixture = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests._narrowing_graph_fixture"
)
compose_narrowing_graph = _graph.compose_narrowing_graph
render_inherency = _graph.render_inherency
carrier, claim = _fixture.carrier, _fixture.claim


def carriers_1():
    return [
        carrier("CA-R-0", "Node"),
        carrier("CA-R-1", "Node/Continuant"),
        carrier("CA-R-2", "Node/Atom"),
        carrier("CA-R-3", "Node/Atom/(.Role := Method)"),
        carrier(
            "CA-R-4",
            "Node/Actor",
            body=claim(
                (
                    "relation(source='Actor', name='NARROWER_"
                    "THAN', target='@Continuant')"
                )
            ),
        ),
        carrier("CA-R-5", "Event Record"),
    ]


def carriers_2():
    return [
        carrier("CA-R-5A", "Node/Continuant//ANECHOIC Framework"),
        carrier("CA-R-6", "Node/Atom.Status"),
        carrier(
            "CA-R-7",
            "Node/Node",
            body=claim(
                (
                    "relation(source='Node', name='NARROWER_T"
                    "HAN', target='Node', source_count='0+')"
                )
            ),
        ),
        carrier("CA-R-8", "CFEL", form="Entity Definition"),
        carrier("CA-R-9", "Carrier", form="Entity Definition"),
        carrier("CA-R-10", "Carrier/File", form="Entity Definition"),
    ]


def carriers_3():
    return [
        carrier(
            "CA-R-11",
            "Carrier/File/Markdown",
            form="Entity Definition",
        ),
        carrier("CA-R-12", "Term", form="Entity Definition"),
        carrier(
            "CA-R-13",
            "CFEL ((NARROWER_THAN)) @Carrier",
            form="Entity Definition",
        ),
        carrier("CA-R-14", "CFEL > Format/bool", form="Entity Definition"),
        carrier("CA-R-15", "Entity/Legacy", form="Entity Definition"),
        carrier(
            "CA-R-16",
            "Node/Atom",
            form="Relation Definition",
            body=claim(
                (
                    "relation(source='Atom', name='NARROWER_T"
                    "HAN', target='@Continuant')"
                )
            ),
        ),
    ]


class NarrowingCases:
    def _declared_paths(
        self,
    ):
        graph, provenance = compose_narrowing_graph(
            carriers_1() + carriers_2() + carriers_3()
        )

        nodes = {row["identity"]: row for row in graph["nodes"]}
        self.assertTrue(
            {
                "Node/Continuant",
                "Node/Atom",
                "Node/Atom/(.Role:=Method)",
                "Node/Actor",
                "CFEL",
                "Carrier",
                "Carrier/File/Markdown",
                "Term",
            }
            <= set(nodes)
        )
        self.assertNotIn("Node/Atom.Status", nodes)
        self.assertNotIn("Node/Continuant//ANECHOIC Framework", nodes)
        self.assertNotIn("Format/bool", nodes)
        self.assertEqual(
            "(.Role:=Method)",
            nodes["Node/Atom/(.Role:=Method)"]["display_name"],
        )
        self.check_edges(graph)
        self.check_rendering(graph, provenance)

    locals()[
        (
            "test_declared_paths_and_explicit_reference_claims_"
            "form_the_only_tree_edges"
        )
    ] = _declared_paths

    def check_edges(self, graph):
        names = {row["id"]: row["identity"] for row in graph["nodes"]}
        edges = {
            (names[row["relation_source"]], names[row["relation_target"]])
            for row in graph["edges"]
        }
        self.assertTrue(
            {
                ("Node/Atom/(.Role:=Method)", "Node/Atom"),
                ("Node/Actor", "Node/Continuant"),
                ("Carrier/File/Markdown", "Carrier/File"),
                ("CFEL", "Carrier"),
            }
            <= edges
        )
        self.assertNotIn(("Node/Node", "Node/Node"), edges)
        self.assertTrue(
            any("CFEL > Format/bool" in row for row in graph["diagnostics"])
        )
        self.assertTrue(
            any("Entity/Legacy" in row for row in graph["diagnostics"])
        )
        self.assertFalse(
            any("ANECHOIC Framework" in row for row in graph["diagnostics"])
        )
        self.assertIn(
            (
                "Event Record: no explicit NARROWER_THAN "
                "parent; rendered as a root."
            ),
            graph["diagnostics"],
        )

    def check_rendering(self, graph, provenance):
        document = render_inherency(
            graph,
            provenance,
            updated_at="2026-11-02 00:00:00 +0400",
            source_selection="controlled Current fixture",
            projection_identity={
                "projection_id": "CA-PROJ-918",
                "named_selection": "Current Nodes",
            },
        )
        self.assertIn("/ (.Role:=Method)", document)
        self.assertIn(
            "Node/Atom/(.Role:=Method)",
            "\n".join(row["identity"] for row in graph["nodes"]),
        )
