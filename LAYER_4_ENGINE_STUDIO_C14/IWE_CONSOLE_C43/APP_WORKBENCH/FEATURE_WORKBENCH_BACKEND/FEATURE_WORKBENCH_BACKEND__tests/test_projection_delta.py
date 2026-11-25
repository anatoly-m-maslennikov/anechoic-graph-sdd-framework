
from __future__ import annotations

import copy
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import compile_content_schema  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (  # noqa: E402
    HeaderColumn,
    HeaderSchema,
)
from KERNEL_MIXER_C59.projection_delta import snapshot  # noqa: E402


class ProjectionDeltaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.schema = HeaderSchema(())
        self.content = compile_content_schema([])

    @staticmethod
    def atom(reference: str, *, path: str | None = None, edges: list[dict] | None = None) -> dict:
        return {
            "source_path": path or f"{reference}.md", "status_group": "Current", "ref": reference,
            "header_json": {}, "content_markdown": "", "content_properties_json": [],
            "relation_edges_json": edges or [],
        }

    @staticmethod
    def edge(source: str, relation: str, target: str, *, derived: bool = False) -> dict:
        return {
            "source_kind": "Atom", "source_ref": source, "relation_type": relation,
            "target_kind": "Atom", "target_ref": target, "derived": derived,
        }

    def project(self, atoms: list[dict], previous=None, schema=None):
        return snapshot(atoms, [], {"CONTAINS"}, schema or self.schema, self.content, previous)

    def test_snapshot_keeps_admitted_maps_and_rejects_wrong_inputs(self):
        original = self.project([self.atom("A")])
        kind = type(original)
        values = (original.atoms, original.scopes, original.graph, original.header_schema,
                  original.content_schema, original.atom_sources)
        copied = kind(*values)
        self.assertTrue(hasattr(kind, "__pydantic_validator__"))
        for name in ("atoms", "scopes", "atom_sources"):
            self.assertIs(getattr(copied, name), getattr(original, name))
        for index in range(len(values)):
            invalid = list(values)
            invalid[index] = []
            with self.subTest(index=index), self.assertRaises(ValueError):
                kind(*invalid)
        for index, wrong in ((2, original.header_schema), (3, original.content_schema), (4, original.graph)):
            invalid = list(values)
            invalid[index] = wrong
            with self.subTest(index=index), self.assertRaises(ValueError):
                kind(*invalid)
        with self.assertRaises(AttributeError):
            copied.atoms = {}

    def test_reuses_only_unchanged_public_atom_rows(self) -> None:
        old_a, unchanged = self.atom("A"), self.atom("B")
        previous = self.project([old_a, unchanged])
        changed_a = self.atom("A")

        current = self.project([changed_a, unchanged], previous)

        self.assertIsNot(previous.atoms[(".", "A.md")], current.atoms[(".", "A.md")])
        self.assertIs(previous.atoms[(".", "B.md")], current.atoms[(".", "B.md")])
        self.assertIs(unchanged, current.atom_sources[(".", "B.md")])

    def test_schema_or_deletion_never_reuses_stale_public_rows(self) -> None:
        first, second = self.atom("A"), self.atom("B")
        previous = self.project([first, second])
        changed_schema = HeaderSchema((HeaderColumn(("kind",), "header.kind", "VARCHAR", True),))

        schema_current = self.project([first, second], previous, changed_schema)
        deleted_current = self.project([first], previous)

        self.assertIsNot(previous.atoms[(".", "A.md")], schema_current.atoms[(".", "A.md")])
        self.assertNotIn((".", "B.md"), deleted_current.atoms)
        self.assertNotIn((".", "B.md"), deleted_current.atom_sources)

    def test_changed_inverse_neighbor_projects_new_relations_without_mutating_previous(self) -> None:
        old_a = self.atom("A", edges=[self.edge("A", "CONTAINS", "B")])
        old_b = self.atom("B")
        previous = self.project([old_a, old_b])
        before = copy.deepcopy(previous.atoms)
        changed_a = self.atom("A", edges=[self.edge("A", "CONTAINS", "B"), self.edge("A", "BLOCKS", "B")])
        changed_b = self.atom("B", edges=[self.edge("B", "IS_BLOCKED_BY", "A", derived=True)])

        current = self.project([changed_a, changed_b], previous)

        self.assertEqual(before, previous.atoms)
        self.assertIsNot(previous.atoms[(".", "B.md")], current.atoms[(".", "B.md")])
        self.assertEqual(
            [{"kind": "Atom", "reference": "A", "derived": True}],
            current.atoms[(".", "B.md")]["header.relations"]["IS_BLOCKED_BY"],
        )


if __name__ == "__main__":
    unittest.main()
