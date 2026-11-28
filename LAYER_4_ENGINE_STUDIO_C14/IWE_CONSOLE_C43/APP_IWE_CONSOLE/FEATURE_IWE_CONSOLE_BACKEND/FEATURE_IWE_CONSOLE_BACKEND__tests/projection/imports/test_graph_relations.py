"""Native graph relation projection tests."""

from __future__ import annotations

import json
import os
from pathlib import Path
import unittest


from . import graph_relations_cases

from KERNEL_MIXER_C59.graph_store import graph_relations  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402


APP_ROOT = Path(__file__).resolve().parents[5]


def extension_directory(root: Path) -> Path:
    """Use the suite-prepared DuckPGQ cache, overridable for local runs."""
    return Path(
        os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            root / ".anechoic_tmp" / "workbench" / "extensions",
        )
    )


class GraphRelationsTests(
    graph_relations_cases.GraphRelationsCases, unittest.TestCase
):
    def setUp(self) -> None:
        self.store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1])
        )
        self.addCleanup(self.store.close)

    def _assert_outgoing_relations(self):
        self.assertEqual(
            {
                ("Atom", "A"): {
                    "CONTAINS": [
                        {"kind": "Atom", "reference": "B", "derived": False}
                    ]
                },
                ("Atom", "B"): {
                    "CONTAINS": [
                        {
                            "kind": "Scope Unit",
                            "reference": "A",
                            "derived": True,
                        }
                    ]
                },
                ("Scope Unit", "A"): {
                    "DEPENDS_ON": [
                        {"kind": "Atom", "reference": "A", "derived": False}
                    ]
                },
            },
            graph_relations(self.store._connection, has_edges=True),
        )

    def test_reads_outgoing_native_edges_with_typed_references(self) -> None:
        self.store.replace(
            [
                self.atom(
                    "A", [self.edge("Atom", "A", "Atom", "B", "CONTAINS")]
                ),
                self.atom(
                    "B",
                    [
                        self.edge(
                            "Atom", "B", "Scope Unit", "A", "CONTAINS", True
                        )
                    ],
                ),
            ],
            [
                self.scope(
                    "A",
                    [self.edge("Scope Unit", "A", "Atom", "A", "DEPENDS_ON")],
                )
            ],
        )

        self._assert_outgoing_relations()

    def test_returns_empty_when_the_native_graph_has_no_edges(self) -> None:
        self.store.replace([self.atom("A", [])], [self.scope("A", [])])
        self.assertEqual(
            {}, graph_relations(self.store._connection, has_edges=True)
        )
        self.assertEqual(
            {}, graph_relations(self.store._connection, has_edges=False)
        )
        self.assertEqual(
            [],
            self.store._connection.execute(
                "SELECT * FROM relations"
            ).fetchall(),
        )
        self.assertEqual(
            ["VARCHAR"] * 5 + ["BOOLEAN"],
            [
                row[1]
                for row in self.store._connection.execute(
                    "DESCRIBE relations"
                ).fetchall()
            ],
        )

    def test_publishes_graph_facts_across_batch_boundaries(self) -> None:
        targets = [f"target-{index:04d}" for index in range(1001)]
        edges = [
            self.edge("Atom", "A", "Atom", ref, "LINKS", index % 2 == 1)
            for index, ref in enumerate(targets)
        ]
        self.store.replace([self.atom("A", [*edges, edges[0]])], [])

        connection = self.store._connection
        self.assertEqual(
            [("Atom", ref) for ref in ["A", *targets]],
            connection.execute(
                "SELECT kind, ref FROM internal.reference ORDER BY rowid"
            ).fetchall(),
        )
        self.assertEqual(
            [(ref, index % 2 == 1) for index, ref in enumerate(targets)],
            connection.execute(
                "SELECT target_ref, derived FROM relations ORDER BY target_ref"
            ).fetchall(),
        )

    def test_flat_relations_follow_rebuild_and_incremental_updates(
        self,
    ) -> None:
        connection = self.store._connection
        query = "SELECT * FROM relations ORDER BY source_ref, target_ref"
        self.assertEqual([], connection.execute(query).fetchall())
        initial = [
            self.atom("A", [self.edge("Atom", "A", "Atom", "B", "LINKS")])
        ]
        self.store.replace(initial, [], relation_types={"LINKS"})
        self.assertEqual(
            [("Atom", "A", "Atom", "B", "LINKS", False)],
            connection.execute(query).fetchall(),
        )
        updated = [
            self.atom(
                "A",
                [self.edge("Atom", "A", "Atom", "C", "LINKS", True)],
                version=2,
            )
        ]
        self.assertTrue(
            self.store.apply(updated, [], relation_types={"LINKS"})
        )
        self.assertEqual(
            [("Atom", "A", "Atom", "C", "LINKS", True)],
            connection.execute(query).fetchall(),
        )
        result = self.store.run(query)
        self.assertEqual(
            [["Atom", "A", "Atom", "C", "LINKS", True]], result["rows"]
        )
        self._assert_flat_type_change(connection, query)

    def test_incremental_apply_updates_graph_without_reinserting_unrelated_atom(
        self,
    ) -> None:
        relation_types = {"CONTAINS", "IS_CONTAINED_BY", "LINKS"}
        initial = [
            self.atom("A", [self.edge("Atom", "A", "Atom", "B", "CONTAINS")]),
            self.atom(
                "B",
                [self.edge("Atom", "B", "Atom", "A", "IS_CONTAINED_BY", True)],
            ),
            self.atom("C", []),
            self.atom("UNRELATED", []),
        ]
        self.store.replace(initial, [], relation_types=relation_types)
        unrelated_before = self.store._connection.execute(
            "SELECT rowid, hash FROM atoms WHERE reference = 'UNRELATED'"
        ).fetchone()

        retargeted = [
            self.atom(
                "A",
                [
                    self.edge("Atom", "A", "Atom", "B", "LINKS"),
                    self.edge("Atom", "A", "Atom", "C", "CONTAINS"),
                ],
                version=2,
            ),
            self.atom("B", []),
            self.atom(
                "C",
                [self.edge("Atom", "C", "Atom", "A", "IS_CONTAINED_BY", True)],
            ),
            self.atom("UNRELATED", []),
        ]
        self.assertTrue(
            self.store.apply(retargeted, [], relation_types=relation_types)
        )

        self._assert_retargeted_edges()
        self._assert_retargeted_relations(unrelated_before)
        self._assert_links_removed(relation_types)

    def _assert_retargeted_edges(self):
        self.assertEqual(
            [("A", "C", False)],
            self.store._connection.execute(
                "FROM GRAPH_TABLE (anechoic MATCH "
                '(source:Reference)-[edge:"CONTAINS"]->(target:Reference) '
                "COLUMNS (source.ref, target.ref, edge.derived))"
            ).fetchall(),
        )
        self.assertEqual(
            [("A", "B", False)],
            self.store._connection.execute(
                "FROM GRAPH_TABLE (anechoic MATCH "
                '(source:Reference)-[edge:"LINKS"]->(target:Reference) '
                "COLUMNS (source.ref, target.ref, edge.derived))"
            ).fetchall(),
        )

    def _assert_retargeted_graph(self):
        self.assertEqual(
            {
                ("Atom", "A"): {
                    "CONTAINS": [
                        {"kind": "Atom", "reference": "C", "derived": False}
                    ],
                    "LINKS": [
                        {"kind": "Atom", "reference": "B", "derived": False}
                    ],
                },
                ("Atom", "C"): {
                    "IS_CONTAINED_BY": [
                        {"kind": "Atom", "reference": "A", "derived": True}
                    ],
                },
            },
            graph_relations(self.store._connection, has_edges=True),
        )

    def _assert_retargeted_relations(self, unrelated_before):
        relations = dict(
            self.store._connection.execute(
                (
                    'SELECT reference, "header.relations" FROM atoms WHERE '
                    "reference IN ('A', 'B', 'C')"
                )
            ).fetchall()
        )
        self.assertEqual(
            {
                "CONTAINS": [
                    {"kind": "Atom", "reference": "C", "derived": False}
                ],
                "LINKS": [
                    {"kind": "Atom", "reference": "B", "derived": False}
                ],
            },
            json.loads(relations["A"]),
        )
        self.assertEqual({}, json.loads(relations["B"]))
        self.assertEqual(
            {
                "IS_CONTAINED_BY": [
                    {"kind": "Atom", "reference": "A", "derived": True}
                ]
            },
            json.loads(relations["C"]),
        )
        self._assert_retargeted_graph()
        self.assertEqual(
            unrelated_before,
            self.store._connection.execute(
                "SELECT rowid, hash FROM atoms WHERE reference = 'UNRELATED'"
            ).fetchone(),
        )

    def _assert_links_removed(self, relation_types):
        links_removed = [
            self.atom(
                "A",
                [self.edge("Atom", "A", "Atom", "C", "CONTAINS")],
                version=3,
            ),
            self.atom("B", []),
            self.atom(
                "C",
                [self.edge("Atom", "C", "Atom", "A", "IS_CONTAINED_BY", True)],
            ),
            self.atom("UNRELATED", []),
        ]
        self.assertTrue(
            self.store.apply(links_removed, [], relation_types=relation_types)
        )
        self.assertEqual(
            [],
            self.store._connection.execute(
                "FROM GRAPH_TABLE (anechoic MATCH "
                '(source:Reference)-[edge:"LINKS"]->(target:Reference) '
                "COLUMNS (source.ref, target.ref))"
            ).fetchall(),
        )


if __name__ == "__main__":
    unittest.main()
