"""Header schema incremental change cases."""

import json
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import atom_fields


class HeaderSchemaDeltaCases:
    def _setup_schema_delta(self):
        initial = [
            self.atom(
                "A",
                {
                    "atom_id": "A",
                    "volatile": "value",
                    "stable": "first",
                    "zero": 0,
                    "enabled": False,
                },
            ),
            self.atom(
                "B",
                {
                    "atom_id": "B",
                    "volatile": "value",
                    "stable": "first",
                    "zero": 0,
                    "enabled": False,
                },
            ),
        ]
        self.store.replace(initial, [])
        retained_row = self.store._connection.execute(
            "SELECT rowid FROM atoms WHERE reference = 'A'"
        ).fetchone()[0]
        return retained_row

    def _assert_stable_delta(self, retained_row):
        normal = [
            self.atom(
                "A",
                {
                    "atom_id": "A",
                    "volatile": "value",
                    "stable": "first",
                    "zero": 0,
                    "enabled": False,
                },
            ),
            self.atom(
                "B",
                {
                    "atom_id": "B",
                    "volatile": "value",
                    "stable": "edited",
                    "zero": 0,
                    "enabled": False,
                },
            ),
        ]
        self.assertTrue(self.store.apply(normal, [], relation_types=set()))
        self.assertFalse(self.store.schema_changed)
        self.assertEqual(
            retained_row,
            self.store._connection.execute(
                "SELECT rowid FROM atoms WHERE reference = 'A'"
            ).fetchone()[0],
        )

    def _assert_empty_delta(self):
        empty = [
            self.atom(
                "A",
                {
                    "atom_id": "A",
                    "volatile": "",
                    "stable": "first",
                    "zero": 0,
                    "enabled": False,
                },
            ),
            self.atom(
                "B",
                {
                    "atom_id": "B",
                    "volatile": None,
                    "stable": "edited",
                    "zero": 0,
                    "enabled": False,
                },
            ),
        ]
        self.assertTrue(self.store.apply(empty, [], relation_types=set()))
        self.assertTrue(self.store.schema_changed)
        self.assertIn(
            "header.volatile",
            atom_fields(self.store._header_schema, self.store._content_schema),
        )
        self.store.replace(empty, [])
        fields = atom_fields(
            self.store._header_schema, self.store._content_schema
        )
        self.assertIn("header.volatile", fields)
        self.assertIn("header.zero", fields)
        self.assertIn("header.enabled", fields)
        self.assertFalse(
            next(
                column.populated
                for column in self.store._header_schema.columns
                if column.name == "header.volatile"
            )
        )
        self._assert_empty_asset()
        return empty

    def _assert_empty_asset(self):
        asset = json.loads(
            (self.database.parent / "projection-schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(
            next(
                column["populated"]
                for column in asset["header_columns"]
                if column["name"] == "header.volatile"
            )
        )

    def test_schema_change_defers_rebuild_but_same_schema_preserves_unaffected_row(
        self,
    ) -> None:
        retained_row = self._setup_schema_delta()
        self._assert_stable_delta(retained_row)
        empty = self._assert_empty_delta()
        self._assert_schema_path_and_type_changes(empty)

    def _assert_schema_path_and_type_changes(self, empty):
        with_empty_path = [
            self.atom(
                "A",
                {
                    "atom_id": "A",
                    "volatile": "",
                    "stable": "first",
                    "zero": 0,
                    "enabled": False,
                },
            ),
            self.atom(
                "B",
                {
                    "atom_id": "B",
                    "volatile": None,
                    "stable": "edited",
                    "zero": 0,
                    "enabled": False,
                    "optional": None,
                },
            ),
        ]
        self.assertTrue(
            self.store.apply(with_empty_path, [], relation_types=set())
        )
        self.assertTrue(self.store.schema_changed)
        self.store.replace(with_empty_path, [])
        self.assertIn(
            "header.optional",
            atom_fields(self.store._header_schema, self.store._content_schema),
        )

        self.assertTrue(self.store.apply(empty, [], relation_types=set()))
        self.assertTrue(self.store.schema_changed)
        self.store.replace(empty, [])
        self.assertNotIn(
            "header.optional",
            atom_fields(self.store._header_schema, self.store._content_schema),
        )

        self._assert_schema_type_change()

    def _assert_schema_type_change(self):
        changed_type = [
            self.atom(
                "A",
                {
                    "atom_id": "A",
                    "volatile": "",
                    "stable": 1,
                    "zero": 0,
                    "enabled": False,
                },
            ),
            self.atom(
                "B",
                {
                    "atom_id": "B",
                    "volatile": None,
                    "stable": 2,
                    "zero": 0,
                    "enabled": False,
                },
            ),
        ]
        self.assertTrue(
            self.store.apply(changed_type, [], relation_types=set())
        )
        self.assertTrue(self.store.schema_changed)
