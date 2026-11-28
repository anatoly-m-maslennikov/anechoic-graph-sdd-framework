"""Source-faithful dynamic Header columns in the Workbench SQL projection."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (  # noqa: E402
    parse_content,
)
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import atom_fields  # noqa: E402
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import QueryStore  # noqa: E402


from .header_schema_delta_cases import HeaderSchemaDeltaCases
from .header_schema_value_cases import HeaderSchemaValueCases


APP_ROOT = Path(__file__).resolve().parents[5]


def extension_directory(root: Path) -> Path:
    """Use the suite-prepared DuckPGQ cache, overridable for local runs."""
    return Path(
        os.environ.get(
            "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
            root / ".anechoic_tmp" / "workbench" / "extensions",
        )
    )


class HeaderSqlColumnsTests(
    HeaderSchemaDeltaCases, HeaderSchemaValueCases, unittest.TestCase
):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.database = (
            Path(self.temporary.name) / "workbench" / "projection.duckdb"
        )
        self.store = QueryStore(
            extension_directory=extension_directory(APP_ROOT.parents[1]),
            database_path=self.database,
        )
        self.addCleanup(self.store.close)

    @staticmethod
    def atom(
        reference: str,
        header: dict,
        *,
        body: str = "## Summary\n\nSummary.\n",
        edges: list[dict] | None = None,
        form: str = "Definition",
        version: int = 1,
    ) -> dict:
        return {
            "source_path": f"source/{reference}.md",
            "status_group": "Current",
            "id": reference,
            "ref": reference,
            "version": version,
            "status": "Active",
            "current_scope_unit": None,
            "claim_target_scope_unit": None,
            "role": "Requirement",
            "form": form,
            "tier": 1,
            "updated_at": None,
            "header_json": header,
            "content_markdown": body,
            "content_properties_json": parse_content(
                body, tolerate_duplicate_siblings=True
            ),
            "relation_edges_json": edges or [],
            "hash": reference,
        }

    @staticmethod
    def edge(source: str, target: str) -> dict:
        return {
            "source_kind": "Atom",
            "source_ref": source,
            "target_kind": "Atom",
            "target_ref": target,
            "relation_type": "CONTAINS",
            "derived": False,
        }

    def _assert_raw_schema(self):
        fields = atom_fields(
            self.store._header_schema, self.store._content_schema
        )
        self.assertTrue(
            {
                "header.atom_id",
                "header.identity.atom_id",
                "header.status",
                "header.state.status",
                "header.enabled",
                "header.zero",
                "header.tags",
                "header.metadata.answer",
                "header.unknown_residue",
                "header.items",
                "header.relations",
            }
            <= set(fields)
        )
        self.assertNotIn("id", fields)
        self.assertNotIn("status", fields)
        values = self.store._connection.execute(
            'SELECT "header.enabled", "header.zero", "header.tags", "header.metadata.answer", '
            '"header.items", "header.identity.atom_id", "header.atom_id" FROM atoms ORDER BY reference'
        ).fetchall()
        self.assertEqual(
            (False, 0, '["one"]', 42, None, None, "CA-R-1"), values[0]
        )
        self.assertEqual(
            (None, None, None, None, '[{"answer":1}]', "CA-R-2", None),
            values[1],
        )
        self._assert_raw_schema_asset()

    def _assert_raw_schema_asset(self):
        asset = json.loads(
            (self.database.parent / "projection-schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertIn(
            {
                "path": ["identity", "atom_id"],
                "name": "header.identity.atom_id",
                "format": "VARCHAR",
                "populated": True,
                "reader": None,
            },
            asset["header_columns"],
        )

    def test_raw_flat_and_nested_paths_build_typed_columns_and_schema_asset(
        self,
    ) -> None:
        flat = self.atom(
            "FLAT",
            {
                "atom_id": "CA-R-1",
                "status": "Active",
                "enabled": False,
                "zero": 0,
                "tags": ["one"],
                "metadata": {"answer": 42},
                "unknown residue": "kept",
                "relations": {},
            },
        )
        nested = self.atom(
            "NESTED",
            {
                "identity": {"atom_id": "CA-R-2"},
                "state": {"status": "Done"},
                "items": [{"answer": 1}],
                "relations": {},
            },
        )

        self.store.replace([flat, nested], [])

        self._assert_raw_schema()

    def test_nested_identity_id_keeps_its_observed_header_column(self) -> None:
        self.store.replace(
            [self.atom("CA-R-3", {"identity": {"id": "CA-R-3"}})], []
        )

        fields = atom_fields(
            self.store._header_schema, self.store._content_schema
        )
        self.assertIn("header.identity.id", fields)
        self.assertNotIn("header.identity.atom_id", fields)
        self.assertEqual(
            ("CA-R-3",),
            self.store._connection.execute(
                "SELECT \"header.identity.id\" FROM atoms WHERE reference = 'CA-R-3'"
            ).fetchone(),
        )

    def test_nested_container_is_queryable_as_json_and_as_leaf_columns(
        self,
    ) -> None:
        rows = [
            self.atom(
                "A", {"context": {"container": {"scope_unit": "CA-SU-00"}}}
            ),
            self.atom("B", {"context": {"container": {"atom": "CA-P-1"}}}),
            self.atom("C", {}),
        ]
        self.store.replace(rows, [])
        self.assertEqual(
            [
                ('{"scope_unit":"CA-SU-00"}', "CA-SU-00", None),
                ('{"atom":"CA-P-1"}', None, "CA-P-1"),
                (None, None, None),
            ],
            self.store._connection.execute(
                'SELECT "header.context.container", "header.context.container.scope_unit", '
                '"header.context.container.atom" FROM atoms ORDER BY reference'
            ).fetchall(),
        )
        self.assertEqual(
            "CA-SU-00",
            self.store._connection.execute(
                "SELECT \"header.context.container\"->>'scope_unit' FROM atoms WHERE reference = 'A'"
            ).fetchone()[0],
        )

        changed = self.atom(
            "A", {"context": {"container": {"scope_unit": "CA-SU-14"}}}
        )
        self.assertTrue(
            self.store.apply([changed, *rows[1:]], [], relation_types=set())
        )
        self.assertFalse(self.store.schema_changed)
        self.assertEqual(
            "CA-SU-14",
            self.store._connection.execute(
                "SELECT \"header.context.container\"->>'scope_unit' FROM atoms WHERE reference = 'A'"
            ).fetchone()[0],
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
