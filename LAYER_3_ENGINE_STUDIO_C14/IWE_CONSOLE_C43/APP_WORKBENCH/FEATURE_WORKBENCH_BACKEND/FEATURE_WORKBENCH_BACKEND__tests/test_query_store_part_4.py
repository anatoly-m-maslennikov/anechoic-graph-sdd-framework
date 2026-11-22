from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
import json
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.errors import (  # noqa: E402
    WorkbenchUnavailableError,
)
from IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.FEATURE_WORKBENCH_BACKEND__tests.query_store_test_support import QueryStoreFixture


class QueryStoreTest(QueryStoreFixture, unittest.TestCase):
    def test_public_graph_table_direct_inverse_cycles_and_typed_identity(self) -> None:
        atoms = [
                self.atom("A", [self.edge("Atom", "A", "Atom", "B")]),
                self.atom("B", [
                    self.edge("Atom", "B", "Atom", "A", derived=True),
                    self.edge("Atom", "B", "Atom", "C"),
                    self.edge("Atom", "B", "Atom", "A@2-draft", "DRAFT_LINK"),
                ]),
                self.atom("C", [self.edge("Atom", "C", "Atom", "A")]),
                self.atom("A@2-draft"),
            ]
        scopes = [self.scope("A", [self.edge("Scope Unit", "A", "Atom", "A", "OWNS")])]
        self.store.replace(atoms, scopes)
        self._assert_graph_direct()
        self._assert_graph_public_rows()
        self._assert_graph_hash_stability(atoms, scopes)
        self._assert_graph_paths()
    def _assert_graph_direct(self):
        direct = self.store.run(
            "FROM GRAPH_TABLE (anechoic "
            "MATCH (a:Reference)-[e:CONTAINS]->(b:Reference) "
            "COLUMNS (a.kind AS source_kind, a.ref AS source_ref, "
            "b.kind AS target_kind, b.ref AS target_ref, "
            "e.relation_type AS relation_type, e.derived AS derived)) "
            "ORDER BY source_ref, target_ref, derived"
        )["rows"]
        self.assertEqual(
            [
                ["Atom", "A", "Atom", "B", "CONTAINS", False],
                ["Atom", "B", "Atom", "A", "CONTAINS", True],
                ["Atom", "B", "Atom", "C", "CONTAINS", False],
                ["Atom", "C", "Atom", "A", "CONTAINS", False],
            ],
            direct,
        )

    def _assert_graph_public_rows(self):
        public_rows = self.store.run(
            'SELECT "relative_path", filename, reference, "header.relations" FROM atoms '
            "WHERE reference IN ('A', 'B') ORDER BY reference"
        )["rows"]
        self.assertEqual(
            [
                [".", "A.md", "A", {"CONTAINS": [{"kind": "Atom", "reference": "B", "derived": False}]}],
                [
                    ".", "B.md", "B",
                    {
                        "CONTAINS": [
                            {"kind": "Atom", "reference": "A", "derived": True},
                            {"kind": "Atom", "reference": "C", "derived": False},
                        ],
                        "DRAFT_LINK": [{"kind": "Atom", "reference": "A@2-draft", "derived": False}],
                    },
                ],
            ],
            [[path, filename, reference, json.loads(relations)]
             for path, filename, reference, relations in public_rows],
        )
        self.assertEqual(
            {},
            json.loads(self.store.run('SELECT "header.relations" FROM atoms WHERE reference = \'A@2-draft\'')["rows"][0][0]),
        )
        self.assertEqual(
            {"OWNS": [{"kind": "Atom", "reference": "A", "derived": False}]},
            json.loads(self.store.run("SELECT relations FROM scope_units WHERE name = 'A'")["rows"][0][0]),
        )

    def _assert_graph_hash_stability(self, atoms, scopes):
        mapping_hashes = self.store.run(
            "SELECT * FROM GRAPH_TABLE (anechoic "
            "MATCH (a:Reference)-[e:CONTAINS]->(b:Reference) "
            "COLUMNS (a.hash AS source_hash, b.hash AS target_hash, e.hash AS edge_hash, "
            "a.ref AS source_ref, b.ref AS target_ref)) "
            "WHERE source_ref = 'A' AND target_ref = 'B'"
        )["rows"]
        self.assertEqual(
            [[
                self.mapping_hash({"kind": "Atom", "ref": "A"}),
                self.mapping_hash({"kind": "Atom", "ref": "B"}),
                self.mapping_hash(self.edge("Atom", "A", "Atom", "B")),
                "A",
                "B",
            ]],
            mapping_hashes,
        )
        self.store.replace(atoms, scopes)
        self.assertEqual(
            mapping_hashes,
            self.store.run(
                "SELECT * FROM GRAPH_TABLE (anechoic "
                "MATCH (a:Reference)-[e:CONTAINS]->(b:Reference) "
                "COLUMNS (a.hash AS source_hash, b.hash AS target_hash, e.hash AS edge_hash, "
                "a.ref AS source_ref, b.ref AS target_ref)) "
                "WHERE source_ref = 'A' AND target_ref = 'B'"
            )["rows"],
        )

    def _assert_graph_paths(self):
        inverse = self.store.run(
            "SELECT * FROM GRAPH_TABLE (anechoic "
            "MATCH (target:Reference)<-[e:CONTAINS]-(source:Reference) "
            "COLUMNS (target.ref AS target_ref, source.ref AS source_ref, e.derived AS derived)) "
            "WHERE target_ref = 'B'"
        )["rows"]
        self.assertEqual([["B", "A", False]], inverse)
        draft = self.store.run(
            "FROM GRAPH_TABLE (anechoic "
            "MATCH (a:Reference)-[e:DRAFT_LINK]->(b:Reference) "
            "COLUMNS (a.kind AS source_kind, a.ref AS source_ref, b.kind AS target_kind, b.ref AS target_ref))"
        )["rows"]
        self.assertEqual([["Atom", "B", "Atom", "A@2-draft"]], draft)
        owned = self.store.run(
            "FROM GRAPH_TABLE (anechoic "
            "MATCH (a:Reference)-[e:OWNS]->(b:Reference) "
            "COLUMNS (a.kind AS source_kind, a.ref AS source_ref, b.kind AS target_kind, b.ref AS target_ref))"
        )["rows"]
        self.assertEqual([["Scope Unit", "A", "Atom", "A"]], owned)
        reachable = self.store.run(
            "WITH RECURSIVE edges AS (FROM GRAPH_TABLE (anechoic "
            "MATCH (a:Reference)-[e:CONTAINS]->(b:Reference) "
            "COLUMNS (a.kind AS source_kind, a.ref AS source_ref, b.kind AS target_kind, b.ref AS target_ref))), "
            "reach(kind, ref) AS (SELECT 'Atom', 'A' UNION "
            "SELECT target_kind, target_ref FROM reach JOIN edges "
            "ON reach.kind = source_kind AND reach.ref = source_ref) "
            "SELECT kind, ref FROM reach ORDER BY ref"
        )["rows"]
        self.assertEqual([["Atom", "A"], ["Atom", "B"], ["Atom", "C"]], reachable)


    def test_native_graph_ctes_select_labels_directions_and_isolated_seed(self) -> None:
        atoms = [
            self.atom("A", [self.edge("Atom", "A", "Atom", "B")]),
            self.atom("B", [
                self.edge("Atom", "B", "Atom", "C"),
                self.edge("Atom", "B", "Atom", "A@2-draft", "DRAFT_LINK"),
            ]),
            self.atom("C", [self.edge("Atom", "C", "Atom", "A")]),
            self.atom("A@2-draft"),
            self.atom("ISOLATED"),
        ]
        self.store.replace(atoms, [])
        multi_label_direction = self.store.run(
            "WITH selected AS (FROM GRAPH_TABLE (anechoic "
            "MATCH (seed:Reference)<-[draft:DRAFT_LINK]-(middle:Reference)-[contains:CONTAINS]->(target:Reference) "
            "WHERE seed.ref = 'A@2-draft' "
            "COLUMNS (seed.kind AS seed_kind, seed.ref AS seed_ref, "
            "middle.kind AS middle_kind, middle.ref AS middle_ref, "
            "target.kind AS target_kind, target.ref AS target_ref))) "
            "SELECT * FROM selected"
        )["rows"]
        self.assertEqual(
            [["Atom", "A@2-draft", "Atom", "B", "Atom", "C"]],
            multi_label_direction,
        )
        isolated = self.store.run(
            "WITH RECURSIVE edges AS (FROM GRAPH_TABLE (anechoic "
            "MATCH (source:Reference)-[e:CONTAINS]->(target:Reference) "
            "COLUMNS (source.kind AS source_kind, source.ref AS source_ref, "
            "target.kind AS target_kind, target.ref AS target_ref))), "
            "reach(kind, ref) AS (SELECT 'Atom', 'ISOLATED' UNION "
            "SELECT target_kind, target_ref FROM reach JOIN edges "
            "ON reach.kind = source_kind AND reach.ref = source_ref) "
            "SELECT kind, ref FROM reach"
        )["rows"]
        self.assertEqual([["Atom", "ISOLATED"]], isolated)
        self._assert_graph_aggregate()
    def _assert_graph_aggregate(self):
        aggregate = self.store.run(
            "WITH graph_edges AS (FROM GRAPH_TABLE (anechoic "
            "MATCH (source:Reference)-[e:CONTAINS]->(target:Reference) "
            "COLUMNS (source.ref AS source_ref, target.ref AS target_ref))) "
            "SELECT graph_edges.source_ref, count(*) AS edge_count FROM graph_edges "
            "JOIN atoms ON atoms.reference = graph_edges.source_ref "
            "WHERE atoms.status_group = 'Current' GROUP BY graph_edges.source_ref "
            "ORDER BY graph_edges.source_ref"
        )["rows"]
        self.assertEqual([["A", 1], ["B", 1], ["C", 1]], aggregate)


    def test_result_delivery_is_lossless_and_refresh_failure_stops_service(self) -> None:
        result = self.store.run(
            "SELECT 9007199254740992::HUGEINT AS wide, 1.20::DECIMAL(4,2) AS decimal, "
            "DATE '2026-11-04' AS day, TIME '01:02:03' AS moment, "
            "TIMESTAMP '2026-11-04 01:02:03' AS stamped, CAST('bin' AS BLOB) AS binary, "
            "[9007199254740992::HUGEINT, 9007199254740993::HUGEINT] AS nested_wide, "
            "[CAST('x' AS BLOB)] AS nested_binary, "
            "{'wide': 9007199254740992::HUGEINT, 'binary': CAST('x' AS BLOB)} AS mapped"
        )["rows"][0]
        self.assertEqual("9007199254740992", result[0])
        self.assertEqual("1.20", result[1])
        self.assertEqual("2026-11-04", result[2])
        self.assertEqual("01:02:03", result[3])
        self.assertEqual("2026-11-04T01:02:03", result[4])
        self.assertEqual("base64:Ymlu", result[5])
        self.assertEqual(["9007199254740992", "9007199254740993"], result[6])
        self.assertEqual(["base64:eA=="], result[7])
        self.assertEqual({"wide": "9007199254740992", "binary": "base64:eA=="}, result[8])
        tables_before = self.store._connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workbench_results'"
        ).fetchall()
        with self.assertRaisesRegex(ValueError, "NaN or infinity"):
            self.store.run("SELECT 'NaN'::DOUBLE")
        self.assertEqual(tables_before, self.store._connection.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'workbench_results'"
        ).fetchall())
        self.assertEqual([[1]], self.store.run("SELECT 1")["rows"])
        with self.assertRaises(RuntimeError):
            self.store.replace([{"source_path": "invalid.md"}], [])
        with self.assertRaisesRegex(RuntimeError, "restart required"):
            self.store.run("SELECT 1")

    def test_internal_management_failure_requires_restart(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaisesRegex(WorkbenchUnavailableError, "restart required"):
            self.store.run("SELECT * FROM drop_property_graph()")
        self.assertIn("query store unavailable", stderr.getvalue())
        with self.assertRaisesRegex(WorkbenchUnavailableError, "restart required"):
            self.store.run("SELECT 1")

