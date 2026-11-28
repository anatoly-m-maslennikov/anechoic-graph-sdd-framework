"""Additional relation registry cases."""

from . import test_relations as fixtures


class RelationRegistryCases:
    def test_only_current_literal_relation_metadata_establishes_inverses(self):
        rows = fixtures.declarations()
        rows[0]["status_group"] = "Draft"
        registered, inverses = fixtures.relation_registry(rows)
        self.assertNotIn("IS_CONTAINED_BY", registered)
        self.assertEqual({}, inverses)
        rows[0]["status_group"] = "Current"
        rows[0]["content_markdown"] += (
            "\n" + fixtures.inverse_call("A", "B") + "\n"
        )
        registered, inverses = fixtures.relation_registry(rows)
        self.assertEqual({"IS_CONTAINED_BY": "CONTAINS"}, inverses)
        self.assertNotIn("A", registered)

    def test_relation_declaration_registers_direct_fact_but_draft_does_not(
        self,
    ):
        declaration = fixtures.relation_declaration(
            "CA-R-1", "IS_WORK_REPORT_FOR"
        )
        declaration["form"] = "Relation Declaration"
        report = fixtures.atom(
            "CA-R-REPORT", relation={"IS_WORK_REPORT_FOR": ["CA-P-TASK"]}
        )
        task = fixtures.atom("CA-P-TASK")

        rows, _ = fixtures.materialize([declaration, report, task], [])
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-R-REPORT",
                "target_kind": "Atom",
                "target_ref": "CA-P-TASK",
                "relation_type": "IS_WORK_REPORT_FOR",
                "derived": False,
            },
            next(row for row in rows if row["ref"] == "CA-R-REPORT")[
                "relation_edges_json"
            ],
        )

        draft = dict(declaration, status_group="Draft")
        self.assertNotIn(
            "IS_WORK_REPORT_FOR", fixtures.relation_registry([draft])[0]
        )
        rows, _ = fixtures.materialize([draft, report, task], [])
        self.assertEqual(
            [],
            next(row for row in rows if row["ref"] == "CA-R-REPORT")[
                "relation_edges_json"
            ],
        )

    def test_inverse_alias_without_own_declaration_normalizes_once(self):
        declaration = fixtures.relation_declaration(
            "CA-R-1",
            "CONTAINS",
            (
                'relation(source="Relation//IS_CONTAINED_BY", '
                'name="IS_INVERSE_ALIAS_FOR", target="Relation//CONTAINS")'
            ),
        )
        parent = fixtures.atom("CA-P-1", relation={"CONTAINS": ["CA-P-2"]})
        child = fixtures.atom(
            "CA-P-2", relation={"IS_CONTAINED_BY": ["CA-P-1"]}
        )
        registry = fixtures.compile_relation_registry(
            [declaration, parent, child]
        )

        self.assertEqual({"CONTAINS"}, set(registry.names))
        self.assertEqual({"IS_CONTAINED_BY": "CONTAINS"}, registry.aliases)
        rows, _ = fixtures.materialize([declaration, parent, child], [])
        edges = next(row for row in rows if row["ref"] == "CA-P-1")[
            "relation_edges_json"
        ]
        self.assertEqual(
            [
                {
                    "source_kind": "Atom",
                    "source_ref": "CA-P-1",
                    "target_kind": "Atom",
                    "target_ref": "CA-P-2",
                    "relation_type": "CONTAINS",
                    "derived": False,
                }
            ],
            edges,
        )
        self.assertEqual(
            {"IS_CONTAINED_BY": ["CA-P-1"]}, child["header_json"]["relations"]
        )

    def test_instance_scoped_literal_metadata_is_warned_and_omitted(self):
        instance_scoped = fixtures.relation_declaration(
            "CA-R-1",
            "DIRECT",
            f"# instances\n{fixtures.inverse_call('DIRECT', 'INVERSE')}\n"
            'relation(source="Relation//LEGACY", name="IS_INVERSE_ALIAS_FOR", target="Relation//DIRECT")\n',
        )
        inverse = fixtures.relation_declaration("CA-R-2", "INVERSE")
        errors = fixtures.StringIO()
        with fixtures.redirect_stderr(errors):
            registry = fixtures.compile_relation_registry(
                [instance_scoped, inverse]
            )
        self.assertEqual({"DIRECT", "INVERSE"}, set(registry.names))
        self.assertEqual({}, registry.inverse)
        self.assertEqual({}, registry.aliases)
        self.assertIn(
            "unsupported Python relation metadata", errors.getvalue()
        )

    def test_ambiguous_literal_inverses_warn_and_keep_direct_facts(self):
        metadata = [
            fixtures.relation_declaration(
                "A", "A", fixtures.inverse_call("A", "B")
            ),
            fixtures.relation_declaration("B", "B"),
            fixtures.relation_declaration(
                "C", "C", fixtures.inverse_call("C", "B")
            ),
            fixtures.relation_declaration(
                "D", "D", fixtures.inverse_call("D", "D")
            ),
            fixtures.relation_declaration(
                "E", "E", fixtures.inverse_call("E", "F")
            ),
            fixtures.relation_declaration(
                "F", "F", fixtures.inverse_call("F", "G")
            ),
            fixtures.relation_declaration("G", "G"),
            fixtures.relation_declaration(
                "J", "J", fixtures.inverse_call("J", "K")
            ),
            fixtures.relation_declaration(
                "K", "K", fixtures.inverse_call("K", "J", reverse=True)
            ),
        ]
        errors = fixtures.StringIO()
        with fixtures.redirect_stderr(errors):
            registered, inverses = fixtures.relation_registry(metadata)
        self.assertEqual({"J": "K"}, inverses)
        self.assertTrue(
            {"A", "B", "C", "D", "E", "F", "G", "J", "K"} <= registered
        )
        self.assertIn("multiple direct owners A, C", errors.getvalue())
        self.assertIn("self-pair", errors.getvalue())
        self.assertIn(
            "derived Relation F is declared direct", errors.getvalue()
        )

        self._check_ambiguous_facts(metadata)

    def _check_ambiguous_facts(self, metadata):
        source = fixtures.atom(
            "CA-P-1", relation={"A": ["CA-P-2"], "J": ["CA-P-3"]}
        )
        with fixtures.redirect_stderr(fixtures.StringIO()):
            rows, _ = fixtures.materialize(
                metadata
                + [source, fixtures.atom("CA-P-2"), fixtures.atom("CA-P-3")],
                [],
            )
        by_ref = {row["ref"]: row for row in rows}
        self._assert_ambiguous_edges(by_ref)

    def _assert_ambiguous_edges(self, by_ref):
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-P-1",
                "target_kind": "Atom",
                "target_ref": "CA-P-2",
                "relation_type": "A",
                "derived": False,
            },
            by_ref["CA-P-1"]["relation_edges_json"],
        )
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-P-1",
                "target_kind": "Atom",
                "target_ref": "CA-P-3",
                "relation_type": "J",
                "derived": False,
            },
            by_ref["CA-P-1"]["relation_edges_json"],
        )
        self.assertEqual([], by_ref["CA-P-2"]["relation_edges_json"])
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "CA-P-3",
                "target_kind": "Atom",
                "target_ref": "CA-P-1",
                "relation_type": "K",
                "derived": True,
            },
            by_ref["CA-P-3"]["relation_edges_json"],
        )

    def test_ambiguous_normalized_header_relation_warns_and_skips_links(self):
        source = fixtures.atom("CA-P-4", relation={"BlOcKs": ["CA-P-5"]})
        errors = fixtures.StringIO()
        with fixtures.redirect_stderr(errors):
            rows, _ = fixtures.materialize(
                [
                    fixtures.relation_declaration("UPPER", "BLOCKS"),
                    fixtures.relation_declaration("LOWER", "blocks"),
                    source,
                    fixtures.atom("CA-P-5"),
                ],
                [],
            )
        self.assertEqual(
            [],
            next(row for row in rows if row["ref"] == "CA-P-4")[
                "relation_edges_json"
            ],
        )
        self.assertIn(
            "CA-P-4.md: ambiguous registered Relation BlOcKs",
            errors.getvalue(),
        )
        self.assertIn(
            "candidates: BLOCKS, blocks; link skipped", errors.getvalue()
        )

    def test_unregistered_relations_and_prose_do_not_create_facts(self):
        row = fixtures.atom(
            "CA-R-4",
            relation={"unknown_relation": ["CA-R-5"]},
            body="CA-R-4 CONTAINS CA-R-5\n",
        )
        rows, _ = fixtures.materialize(fixtures.declarations() + [row], [])
        self.assertEqual([], rows[-1]["relation_edges_json"])
