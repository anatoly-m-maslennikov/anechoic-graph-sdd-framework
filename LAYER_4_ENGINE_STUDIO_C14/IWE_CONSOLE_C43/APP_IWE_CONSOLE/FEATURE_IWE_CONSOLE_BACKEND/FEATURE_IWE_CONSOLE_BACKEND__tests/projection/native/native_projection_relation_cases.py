"""Native projection test cases."""

from . import test_native_projection as fixtures


class NativeProjectionRelationCases:
    def test_authored_relation_to_config_exact_reference(self):
        row = {
            "ref": "AN-P-1",
            "header_json": {"relations": {"REFERENCES": ["AN-C-2@3-draft"]}},
        }
        edges = list(fixtures.native_projection._authored_edges(row))
        self.assertEqual(
            ("Atom", "AN-C-2@3-draft"),
            (edges[0]["target_kind"], edges[0]["target_ref"]),
        )

    def test_historical_relations_project_to_declared_successors(self):
        relations = {
            "ADVANCES": ["AN-S-2@3-draft"],
            "SERVES": ["AN-S-2@3-draft"],
            "IS_ADVANCED_BY": ["AN-S-3"],
            "REFINES": ["AN-S-4"],
            "IS_REFINED_BY": ["AN-S-5"],
        }
        row = {
            "ref": "AN-S-1",
            "header_json": {"relations": relations},
            "content_markdown": "Archived text",
        }
        inverse = {
            "SERVES": "IS_SERVED_BY",
            "IS_SERVED_BY": "SERVES",
            "CONTRIBUTES_TO": "RECEIVES_CONTRIBUTION_FROM",
            "RECEIVES_CONTRIBUTION_FROM": "CONTRIBUTES_TO",
        }
        capture = fixtures.NativeCapture([row], [], {})
        projected = fixtures.native_projection._projected_rows(
            capture, set(inverse), inverse
        )[0]
        edges = projected["relation_edges_json"]
        self.assertEqual(8, len(edges))
        self.assertEqual(
            {
                ("SERVES", "AN-S-2@3-draft"),
                ("IS_SERVED_BY", "AN-S-3"),
                ("CONTRIBUTES_TO", "AN-S-4"),
                ("RECEIVES_CONTRIBUTION_FROM", "AN-S-5"),
            },
            {
                (e["relation_type"], e["target_ref"])
                for e in edges
                if not e["derived"]
            },
        )
        self._assert_historical_inverse(edges, relations, row, projected)

    def _assert_historical_inverse(self, edges, relations, row, projected):
        self.assertIn(
            ("IS_SERVED_BY", "AN-S-2@3-draft", "AN-S-1"),
            {
                (e["relation_type"], e["source_ref"], e["target_ref"])
                for e in edges
                if e["derived"]
            },
        )
        self.assertIs(relations, row["header_json"]["relations"])
        self.assertEqual("Archived text", projected["content_markdown"])

    def test_declared_historical_relation_is_not_rewritten(self):
        row = {
            "ref": "AN-S-1",
            "header_json": {"relations": {"ADVANCES": ["AN-S-2"]}},
        }
        capture = fixtures.NativeCapture([row], [], {})
        projected = fixtures.native_projection._projected_rows(
            capture, {"ADVANCES", "SERVES"}, {}
        )[0]
        self.assertEqual(
            "ADVANCES", projected["relation_edges_json"][0]["relation_type"]
        )
        with self.assertRaisesRegex(
            ValueError, "Undeclared native relation: ADVANCES"
        ):
            fixtures.native_projection._projected_rows(capture, set(), {})

    def test_old_contribution_inverses_project_to_has_contribution(self):
        row = {
            "ref": "AN-S-1",
            "header_json": {
                "relations": {
                    "IS_REFINED_BY": ["AN-S-2"],
                    "RECEIVES_CONTRIBUTION_FROM": ["AN-S-2"],
                }
            },
        }
        inverse = {
            "CONTRIBUTES_TO": "HAS_CONTRIBUTION",
            "HAS_CONTRIBUTION": "CONTRIBUTES_TO",
        }
        (projected,) = fixtures.native_projection._projected_rows(
            fixtures.NativeCapture([row], [], {}), set(inverse), inverse
        )
        self.assertEqual(
            [
                ("HAS_CONTRIBUTION", "AN-S-1", "AN-S-2", False),
                ("CONTRIBUTES_TO", "AN-S-2", "AN-S-1", True),
            ],
            [
                (
                    edge["relation_type"],
                    edge["source_ref"],
                    edge["target_ref"],
                    edge["derived"],
                )
                for edge in projected["relation_edges_json"]
            ],
        )
