"""Additional graph delta and rollback cases."""

import copy
from unittest.mock import patch
from dataclasses import replace
from KERNEL_MIXER_C59.index_delta import MaterializationDelta
from KERNEL_MIXER_C59.projection_delta import apply
from KERNEL_MIXER_C59.graph_store import graph_relations
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    ContentSchema,
    DeclarationSource,
)


class GraphDeltaCases:
    def test_delta_moves_public_atom_without_reinserting_its_reference(
        self,
    ) -> None:
        old = self.atom("A", path="old/A.md")
        self.replace([old])
        moved = self.atom("A", version=2, path="new/A.md")

        self.apply_delta(
            [moved],
            MaterializationDelta(
                {"old/A.md": old}, {"new/A.md": moved}, {}, {}
            ),
        )

        self.assertEqual(
            [("new", "A.md", "A")],
            self.store._connection.execute(
                'SELECT "relative_path", filename, reference FROM atoms'
            ).fetchall(),
        )
        self.assertEqual(
            [("Atom", "A")],
            self.store._connection.execute(
                "SELECT kind, ref FROM internal.reference"
            ).fetchall(),
        )

    def test_delta_accepts_content_schema_provenance_only_change(self) -> None:
        atom = self.atom("A")
        self.replace([atom])
        previous = self.store._projection
        assert previous is not None
        previous_schema = ContentSchema(
            (), (), (DeclarationSource("A", 1, "A.md"),)
        )
        current_schema = ContentSchema(
            (), (), (DeclarationSource("A", 2, "A.md"),)
        )
        previous = replace(previous, content_schema=previous_schema)
        connection = self.store._connection
        connection.execute("BEGIN TRANSACTION")
        current, change = apply(
            connection,
            previous,
            [atom],
            [],
            self.relation_types,
            self.store._header_schema,
            current_schema,
            delta=MaterializationDelta({}, {}, {}, {}),
        )
        connection.execute("COMMIT")

        self.assertEqual(0, change.inserted_atoms)
        self.assertEqual(current_schema, current.content_schema)

    def test_rollback_does_not_mutate_previous_snapshot(self) -> None:
        old = self.atom("A")
        self.replace([old])
        previous = self.store._projection
        assert previous is not None
        before = copy.deepcopy(previous)
        new = self.atom(
            "A", edges=[self.edge("A", "CONTAINS", "B")], version=2
        )
        connection = self.store._connection
        connection.execute("BEGIN TRANSACTION")
        current, _ = apply(
            connection,
            previous,
            [new],
            [],
            self.relation_types,
            self.store._header_schema,
            self.store._content_schema,
            delta=MaterializationDelta({"A.md": old}, {"A.md": new}, {}, {}),
        )
        connection.execute("ROLLBACK")

        self.assertEqual(before, previous)
        self.assertIn((".", "A.md"), current.atoms)
        self.assertEqual({}, graph_relations(connection, has_edges=True))

    def test_delta_keeps_dangling_target_and_accepts_its_reappearance(
        self,
    ) -> None:
        source = self.atom("A", edges=[self.edge("A", "CONTAINS", "B")])
        target = self.atom("B")
        self.replace([source, target])

        self.apply_delta(
            [source], MaterializationDelta({"B.md": target}, {}, {}, {})
        )
        self.assertEqual(
            [("Atom", "B")],
            self.store._connection.execute(
                "SELECT kind, ref FROM internal.reference WHERE ref = 'B'"
            ).fetchall(),
        )
        self.assertEqual(
            [],
            self.store._connection.execute(
                "SELECT * FROM atoms WHERE reference = 'B'"
            ).fetchall(),
        )

        reappeared = self.atom("B", version=2)
        self.apply_delta(
            [source, reappeared],
            MaterializationDelta({}, {"B.md": reappeared}, {}, {}),
        )
        self.assertEqual(
            [("B",)],
            self.store._connection.execute(
                "SELECT reference FROM atoms WHERE reference = 'B'"
            ).fetchall(),
        )
        self.assertEqual(
            [("Atom", "B")],
            self.store._connection.execute(
                "SELECT kind, ref FROM internal.reference WHERE ref = 'B'"
            ).fetchall(),
        )

    def _assert_archived_removal(self, changed):
        self.apply_delta(
            [],
            MaterializationDelta(
                {changed["source_path"]: changed}, {}, {}, {}
            ),
        )
        self.assertEqual(
            self.store._connection.execute(
                "SELECT count(*) FROM atoms"
            ).fetchone(),
            (0,),
        )

    def _assert_delta_parity(self, expected, current):
        self.assertEqual(expected.atoms, current.atoms)
        self.assertEqual(expected.scopes, current.scopes)
        self.assertEqual(expected.graph.references, current.graph.references)
        self.assertEqual(expected.graph.edges, current.graph.edges)
        self.assertEqual(
            {
                ("Atom", "A"): {
                    "CONTAINS": [
                        {"kind": "Atom", "reference": "C", "derived": False}
                    ]
                },
                ("Atom", "C"): {
                    "IS_CONTAINED_BY": [
                        {"kind": "Atom", "reference": "A", "derived": True}
                    ]
                },
            },
            graph_relations(self.store._connection, has_edges=True),
        )

    def _assert_archived_shape(self, previous, key):
        self.assertEqual(
            set(previous.atoms[key]),
            {"relative_path", "filename", "status_group", "reference", "hash"},
        )

    def _apply_without_full_scan(self, updated, delta):
        with (
            patch(
                "KERNEL_MIXER_C59.projection_delta.graph_state",
                side_effect=AssertionError(
                    "ordinary delta must not scan full graph state"
                ),
            ),
            patch(
                "KERNEL_MIXER_C59.projection_delta._changed_keys",
                side_effect=AssertionError(
                    "ordinary delta must not scan all public rows"
                ),
            ),
        ):
            current, _ = self.apply_delta(updated, delta)
        return current
