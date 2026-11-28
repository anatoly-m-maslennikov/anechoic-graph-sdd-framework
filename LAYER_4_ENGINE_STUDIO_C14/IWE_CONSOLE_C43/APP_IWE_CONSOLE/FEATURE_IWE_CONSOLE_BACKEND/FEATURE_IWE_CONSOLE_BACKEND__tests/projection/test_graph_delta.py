"""Incremental Workbench projection checks against real DuckPGQ."""

from __future__ import annotations

from pathlib import Path
import os
import unittest
from pydantic import ValidationError


from .graph_delta_cases import GraphDeltaCases


from KERNEL_MIXER_C59.index_delta import MaterializationDelta  # noqa: E402
from KERNEL_MIXER_C59.projection_delta import apply, snapshot  # noqa: E402
from KERNEL_MIXER_C59.graph_store import graph_relations  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402


APP_ROOT = Path(__file__).resolve().parents[4]


def extension_directory(root: Path) -> Path:
    """Use the suite-prepared DuckPGQ cache, overridable for local runs."""
    return Path(
        os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            root / ".anechoic_tmp" / "workbench" / "extensions",
        )
    )


class GraphDeltaTest(GraphDeltaCases, unittest.TestCase):
    relation_types = {"CONTAINS", "IS_CONTAINED_BY"}

    def setUp(self) -> None:
        self.store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1])
        )
        self.addCleanup(self.store.close)

    @staticmethod
    def edge(
        source: str, relation: str, target: str, *, derived: bool = False
    ) -> dict:
        return {
            "source_kind": "Atom",
            "source_ref": source,
            "target_kind": "Atom",
            "target_ref": target,
            "relation_type": relation,
            "derived": derived,
        }

    @staticmethod
    def atom(
        reference: str,
        *,
        edges: list[dict] | None = None,
        version: int = 1,
        path: str | None = None,
    ) -> dict:
        return {
            "source_path": path or f"{reference}.md",
            "status_group": "Current",
            "id": reference,
            "ref": reference,
            "version": version,
            "status": "Active",
            "current_scope_unit": None,
            "claim_target_scope_unit": None,
            "role": "Requirement",
            "form": "Declaration",
            "tier": 1,
            "updated_at": None,
            "header_json": {},
            "content_markdown": "",
            "content_properties_json": [],
            "relation_edges_json": edges or [],
            "hash": reference,
        }

    def replace(self, atoms: list[dict]) -> None:
        self.store.replace(atoms, [], relation_types=self.relation_types)

    def apply_delta(
        self,
        atoms: list[dict],
        delta: MaterializationDelta,
    ) -> tuple[object, object]:
        previous = self.store._projection
        assert previous is not None
        connection = self.store._connection
        connection.execute("BEGIN TRANSACTION")
        try:
            current, change = apply(
                connection,
                previous,
                atoms,
                [],
                self.relation_types,
                self.store._header_schema,
                self.store._content_schema,
                delta=delta,
            )
            connection.execute("COMMIT")
        except BaseException:
            connection.execute("ROLLBACK")
            raise
        self.store._projection = current
        return current, change

    def test_delta_requires_structured_rows_without_exposing_values(
        self,
    ) -> None:
        with self.assertRaises(ValidationError) as error:
            MaterializationDelta({"row": "private-value"}, {}, {}, {})
        self.assertNotIn("private-value", str(error.exception))

    def test_archived_snapshot_is_lean_but_changed_rows_are_reinserted(
        self,
    ) -> None:
        archived = self.atom("CA-R-123@1", path="archive/CA-R-123@1.md")
        archived.update(
            status_group="Archived",
            header_json={"atom_id": "CA-R-123", "version": 1},
            _graph_excluded=True,
            _carrier_relation_edges_json=[],
        )
        self.replace([archived])
        previous = self.store._projection
        assert previous is not None
        key = ("archive", "CA-R-123@1.md")
        self._assert_archived_shape(previous, key)
        self.assertEqual(
            self.store._connection.execute(
                'SELECT "header.atom_id" FROM atoms'
            ).fetchone(),
            ("CA-R-123",),
        )
        changed = dict(
            archived, header_json={"atom_id": "CA-R-123", "version": 2}
        )
        self.apply_delta(
            [changed],
            MaterializationDelta(
                {archived["source_path"]: archived},
                {changed["source_path"]: changed},
                {},
                {},
            ),
        )
        self.assertEqual(
            self.store._connection.execute(
                'SELECT "header.version" FROM atoms'
            ).fetchone(),
            (2,),
        )
        self.assertEqual(
            set(self.store._projection.atoms[key]),
            {"relative_path", "filename", "status_group", "reference", "hash"},
        )
        self._assert_archived_removal(changed)

    def test_delta_has_full_projection_parity_without_graph_state_scan(
        self,
    ) -> None:
        old_a = self.atom("A", edges=[self.edge("A", "CONTAINS", "B")])
        old_b = self.atom(
            "B", edges=[self.edge("B", "IS_CONTAINED_BY", "A", derived=True)]
        )
        self.replace([old_a, old_b, self.atom("UNRELATED")])
        previous = self.store._projection
        assert previous is not None
        new_a = self.atom(
            "A", edges=[self.edge("A", "CONTAINS", "C")], version=2
        )
        new_b = self.atom("B")
        new_c = self.atom(
            "C", edges=[self.edge("C", "IS_CONTAINED_BY", "A", derived=True)]
        )
        updated = [new_a, new_b, new_c, self.atom("UNRELATED")]
        expected = snapshot(
            updated,
            [],
            self.relation_types,
            self.store._header_schema,
            self.store._content_schema,
        )
        delta = MaterializationDelta(
            {"A.md": old_a, "B.md": old_b},
            {"A.md": new_a, "B.md": new_b, "C.md": new_c},
            {},
            {},
        )
        current = self._apply_without_full_scan(updated, delta)

        self._assert_delta_parity(expected, current)

    def test_delta_replaces_direct_and_inverse_only_rows(self) -> None:
        old_a = self.atom("A", edges=[self.edge("A", "CONTAINS", "B")])
        old_b = self.atom(
            "B", edges=[self.edge("B", "IS_CONTAINED_BY", "A", derived=True)]
        )
        self.replace([old_a, old_b, self.atom("UNRELATED")])
        new_a = self.atom(
            "A", edges=[self.edge("A", "CONTAINS", "C")], version=2
        )
        new_b = self.atom("B")
        new_c = self.atom(
            "C", edges=[self.edge("C", "IS_CONTAINED_BY", "A", derived=True)]
        )

        self.apply_delta(
            [new_a, new_b, new_c, self.atom("UNRELATED")],
            MaterializationDelta(
                {"A.md": old_a, "B.md": old_b},
                {"A.md": new_a, "B.md": new_b, "C.md": new_c},
                {},
                {},
            ),
        )
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
        self.assertEqual(
            [("UNRELATED",)],
            self.store._connection.execute(
                "SELECT reference FROM atoms WHERE reference = 'UNRELATED'"
            ).fetchall(),
        )

    def test_delta_preserves_and_removes_self_loop_reference_counts(
        self,
    ) -> None:
        old = self.atom("A", edges=[self.edge("A", "CONTAINS", "A")])
        self.replace([old])
        previous = self.store._projection
        assert previous is not None
        revised = self.atom("A", version=2)

        current, _ = self.apply_delta(
            [revised],
            MaterializationDelta({"A.md": old}, {"A.md": revised}, {}, {}),
        )
        self.assertIs(
            previous.graph.edges["IS_CONTAINED_BY"],
            current.graph.edges["IS_CONTAINED_BY"],
        )
        self.assertEqual(
            [("Atom", "A")],
            self.store._connection.execute(
                "SELECT kind, ref FROM internal.reference"
            ).fetchall(),
        )
        self.apply_delta(
            [], MaterializationDelta({"A.md": revised}, {}, {}, {})
        )
        self.assertEqual(
            [],
            self.store._connection.execute(
                "SELECT kind, ref FROM internal.reference"
            ).fetchall(),
        )


if __name__ == "__main__":
    unittest.main()
