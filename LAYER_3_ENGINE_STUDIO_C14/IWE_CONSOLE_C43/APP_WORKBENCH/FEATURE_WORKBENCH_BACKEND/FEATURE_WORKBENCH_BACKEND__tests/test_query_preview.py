from __future__ import annotations

import os
from pathlib import Path
import unittest


APP_ROOT = Path(__file__).resolve().parents[3]

from KERNEL_MIXER_C59.query_store import QueryStore  # noqa: E402


def extension_directory(root: Path) -> Path:
    """Use the suite-prepared DuckPGQ cache, overridable for local runs."""
    return Path(os.environ.get(
        "ANECHOIC_DUCKPGQ_EXTENSION_DIRECTORY",
        root / ".anechoic_tmp" / "workbench" / "extensions",
    ))


def atom(ref: str, edges: list[dict] | None = None) -> dict:
    return {
        "source_path": f"{ref}.md", "status_group": "Current", "id": ref, "ref": ref,
        "version": 1, "status": "Active", "current_scope_unit": None,
        "claim_target_scope_unit": None, "role": "Requirement", "form": "Declaration",
        "tier": 1, "updated_at": None,
        "header_json": {"atom_id": ref, "version": 1, "status": "Active"},
        "content_markdown": "# Claim\n", "content_properties_json": [],
        "relation_edges_json": edges or [], "hash": f"atom-{ref}",
    }


def edge(source: str, target: str) -> dict:
    return {
        "source_kind": "Atom", "source_ref": source, "target_kind": "Atom",
        "target_ref": target, "relation_type": "CONTAINS", "derived": False,
    }


class QueryPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = QueryStore(extension_directory=extension_directory(APP_ROOT.parents[1]))

    def tearDown(self) -> None:
        self.store.close()

    def test_preview_caps_native_result_without_changing_public_sql(self) -> None:
        sql = "WITH values_cte AS (SELECT range AS value FROM range(5)) SELECT value FROM values_cte ORDER BY value DESC"

        result = self.store.run(sql, preview=2)

        self.assertEqual(sql, result["sql"])
        self.assertEqual([[4], [3]], result["rows"])
        self.assertEqual(2, result["row_count"])
        self.assertEqual(sql, self.store.page(result["query_id"], 0)["sql"])

    def test_terminal_line_comment_preserves_graph_query_and_preview(self) -> None:
        self.store.replace([atom("A", [edge("A", "B")]), atom("B")], [])
        graph = ("FROM GRAPH_TABLE (anechoic MATCH (a:Reference)-[e:CONTAINS]->(b:Reference) "
                 "COLUMNS (a.ref AS source, b.ref AS target)) ORDER BY 2 -- terminal comment")
        for ending, preview in (("", None), ("\n", None), ("", 2), ("\n", 2)):
            sql = graph + ending
            with self.subTest(ending=ending, preview=preview):
                result = self.store.run(sql, preview=preview)
                self.assertEqual(sql, result["sql"])
                self.assertEqual([["A", "B"]], result["rows"])
                self.assertEqual(sql, self.store.page(result["query_id"], 0)["sql"])

    def test_preview_preserves_existing_limit_and_validates_value(self) -> None:
        self.assertEqual(
            [[0], [1]],
            self.store.run("SELECT range AS value FROM range(10) LIMIT 2", preview=5)["rows"],
        )
        self.assertEqual([], self.store.run("SELECT 1", preview=0)["rows"])
        for value in (True, -1, 1.5, "1"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "preview"):
                    self.store.run("SELECT 1", preview=value)
