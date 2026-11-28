"""Additional current instance graph cases."""

from importlib import import_module

graph_for = import_module(
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH."
    "GENERATE_ENTITY_GRAPH__tests.graphs.instances._instance_graph_fixture"
).graph_for


class InstanceGraphCases:
    def test_classification_is_one_direct_fact_with_ordinary_endpoints(
        self,
    ) -> None:
        first, _ = graph_for("Entity >| Classification")
        second, _ = graph_for("Classification |< Entity")
        self.assertEqual(first["edges"], second["edges"])
        self.assertEqual("HAS_AXIS", first["edges"][0]["kind"])
        self.assertTrue(all("kind" not in row for row in first["nodes"]))

    def test_formats_counts_and_declared_reference_do_not_create_terms(
        self,
    ) -> None:
        graph, _ = graph_for("X:Value[Text]{1+}")
        self.assertEqual(
            {"X", "X:Value"}, {row["identity"] for row in graph["nodes"]}
        )
        value = next(
            row for row in graph["nodes"] if row["identity"] == "X:Value"
        )
        self.assertEqual("Text", value["value_format"])
        self.assertEqual(
            {"minimum": 1, "maximum": None}, value["value_cardinality"]
        )
        reference, _ = graph_for("@(Root/X.Property)")
        self.assertEqual(
            ["Root/X.Property"],
            [row["identity"] for row in reference["nodes"]],
        )
        self.assertEqual([], reference["edges"])

    def test_named_relation_retains_canonical_direct_direction_and_counts(
        self,
    ) -> None:
        graph, _ = graph_for("Left {0+}((USES)){1} Right")
        self.assertEqual("USES", graph["edges"][0]["kind"])
        self.assertEqual(
            {"minimum": 0, "maximum": None},
            graph["edges"][0]["forward_cardinality"],
        )
