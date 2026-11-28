"""Header value, declaration, and relation cases."""

import json
from unittest.mock import patch
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import (
    atom_fields,
    infer_header_schema,
    WorkbenchUnavailableError,
)
from KERNEL_MIXER_C59.index_delta import MaterializationDelta
from ..content_schema_fixture import SUMMARY_CLAIM, python_claim_body


class HeaderSchemaValueCases:
    def _assert_mixed_values(self):
        values = self.store._connection.execute(
            'SELECT "header.mixed" FROM atoms ORDER BY reference'
        ).fetchall()
        self.assertEqual(
            [{"child": 2}, [], {}, 1, ""],
            [json.loads(value[0]) for value in values],
        )
        self.assertEqual(
            [(2,)],
            self.store._connection.execute(
                "SELECT \"header.mixed.child\" FROM atoms WHERE reference = 'group'"
            ).fetchall(),
        )
        self.assertEqual(
            [(None,), ("{}",), (None,), ('""',), ("[]",)],
            self.store._connection.execute(
                'SELECT "header.all_empty" FROM atoms ORDER BY reference'
            ).fetchall(),
        )

    def test_mixed_empty_values_keep_their_native_values_without_conversion_failure(
        self,
    ) -> None:
        rows = [
            self.atom("number", {"mixed": 1, "all_empty": ""}),
            self.atom("text", {"mixed": "", "all_empty": []}),
            self.atom("list", {"mixed": [], "all_empty": {}}),
            self.atom("map", {"mixed": {}, "all_empty": None}),
            self.atom(
                "group",
                {
                    "mixed": {"child": 2},
                    "group_only": {"child": 2},
                    "empty_map": {},
                },
            ),
        ]

        self.store.replace(rows, [])

        fields = atom_fields(
            self.store._header_schema, self.store._content_schema
        )
        self.assertIn("header.mixed", fields)
        self.assertIn("header.mixed.child", fields)
        self.assertIn("header.all_empty", fields)
        self.assertIn("header.empty_map", fields)
        self.assertIn("header.group_only.child", fields)
        self.assertNotIn("header.group_only", fields)
        self._assert_mixed_values()

    def test_declaration_provenance_delta_keeps_the_table_and_updates_the_schema_asset(
        self,
    ) -> None:
        declaration_body = python_claim_body(SUMMARY_CLAIM)
        first = self.atom(
            "CA-R-DECL",
            {"atom_id": "CA-R-DECL", "version": 1},
            body=declaration_body,
            form="Declaration",
            version=1,
        )
        ordinary = self.atom("CA-R-ORDINARY", {"atom_id": "CA-R-ORDINARY"})
        self.store.replace([first, ordinary], [])
        retained_row = self.store._connection.execute(
            "SELECT rowid FROM atoms WHERE reference = 'CA-R-ORDINARY'"
        ).fetchone()[0]
        later = {
            **first,
            "version": 2,
            "header_json": {"atom_id": "CA-R-DECL", "version": 2},
        }

        self.assertTrue(
            self.store.apply([later, ordinary], [], relation_types=set())
        )

        self.assertFalse(self.store.schema_changed)
        self.assertEqual(
            retained_row,
            self.store._connection.execute(
                "SELECT rowid FROM atoms WHERE reference = 'CA-R-ORDINARY'"
            ).fetchone()[0],
        )
        self.assertEqual(
            ("Summary.",),
            self.store._connection.execute(
                "SELECT \"content.summary\" FROM atoms WHERE reference = 'CA-R-ORDINARY'"
            ).fetchone(),
        )
        content_asset = json.loads(
            (self.database.parent / "content-schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            2, content_asset["content_declaration_sources"][0]["version"]
        )

    def test_materialized_relations_and_normalized_name_collisions_are_explicit(
        self,
    ) -> None:
        self.store.replace(
            [
                self.atom(
                    "A",
                    {"atom_id": "A", "relations": {}},
                    edges=[self.edge("A", "B")],
                ),
                self.atom("B", {"atom_id": "B", "relations": {}}),
            ],
            [],
        )
        relations = self.store._connection.execute(
            "SELECT \"header.relations\" FROM atoms WHERE reference = 'A'"
        ).fetchone()[0]
        self.assertEqual(
            {
                "CONTAINS": [
                    {"kind": "Atom", "reference": "B", "derived": False}
                ]
            },
            json.loads(relations),
        )
        with self.assertRaisesRegex(ValueError, "collision"):
            infer_header_schema(
                [{"header_json": {"same-name": "a", "same_name": "b"}}]
            )

    def test_failed_delta_write_does_not_publish_candidate_header_state(
        self,
    ) -> None:
        original = self.atom("A", {"atom_id": "A", "stable": "before"})
        unchanged = self.atom("B", {"atom_id": "B", "stable": "unchanged"})
        self.store.replace([original, unchanged], [])
        previous_state = self.store._header_state
        previous_schema = self.store._header_schema
        updated = self.atom(
            "A", {"atom_id": "A", "stable": "after"}, version=2
        )
        delta = MaterializationDelta(
            old_atoms={"source/A.md": original},
            new_atoms={"source/A.md": updated},
            old_scopes={},
            new_scopes={},
        )

        with (
            patch(
                "KERNEL_MIXER_C59.query_projection.apply_projection_delta",
                side_effect=RuntimeError("write failed"),
            ),
            self.assertRaises(WorkbenchUnavailableError),
        ):
            self.store.apply(
                [updated, unchanged], [], relation_types=set(), delta=delta
            )

        self.assertIs(previous_state, self.store._header_state)
        self.assertIs(previous_schema, self.store._header_schema)
