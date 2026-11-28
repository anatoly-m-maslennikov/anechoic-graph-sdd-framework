from __future__ import annotations

from pathlib import Path
import unittest

import yaml  # noqa: F401

from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import projected_rows  # noqa: E402, F401
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import materialize  # noqa: E402, F401
from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import infer_header_schema  # noqa: E402, F401
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__shared import (  # noqa: E402
    SourceReader,
    expected_carrier,  # noqa: F401
)
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.sources.audit.test_source_schema_audit import (
    auditor,  # noqa: F401
)  # noqa: E402


from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.sources._source_reader_fixture import (
    SourceReaderFixture,
)  # noqa: E402


from .source_reader_root_cases import SourceReaderRootCases
from .source_reader_status_cases import SourceReaderStatusCases


APP_ROOT = Path(__file__).resolve().parents[5]
TOOLS_ROOT = APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS"

ATOM_COLUMNS = (
    "source_path",
    "status_group",
    "id",
    "ref",
    "version",
    "status",
    "current_scope_unit",
    "claim_target_scope_unit",
    "role",
    "form",
    "tier",
    "updated_at",
    "header_json",
    "_content_bytes",
    "content_properties_json",
    "relation_edges_json",
    "hash",
)
SCOPE_COLUMNS = (
    "name",
    "scope_unit_id",
    "parent_name",
    "declared_label",
    "ordered",
    "order_number",
    "declaration_source_path",
    "declaration_version",
    "relation_edges_json",
    "hash",
)
ROLES = (
    "01_concern",
    "02_analysis",
    "03_plan",
    "04_requirement",
    "05_method",
    "06_evaluation",
    "07_delivery",
    "08_implementation",
    "09_operations",
)


class SourceReaderTests(
    SourceReaderRootCases,
    SourceReaderStatusCases,
    SourceReaderFixture,
    unittest.TestCase,
):
    def test_model_rows_do_not_restore_an_archived_declaration_from_a_copy(
        self,
    ) -> None:
        current = self._write_atom(
            "MAIN", "04_requirement", "CA-R-900.md", atom_id="CA-R-900"
        )
        archived = self._path(
            "MAIN", "04_requirement", "CA-R-900@1.md", "099_archived"
        )
        current.rename(archived)
        copied_row = {
            "id": "CA-R-900",
            "ref": "CA-R-900",
            "source_path": "installed/CA-R-900.md",
        }
        other_copy = {
            "id": "CA-R-901",
            "ref": "CA-R-901",
            "source_path": "installed/CA-R-901.md",
        }
        reader = SourceReader(self.root, include_archived=False)
        reader.capture()

        rows = reader.model_rows(
            [copied_row, other_copy],
            lambda row: row["id"] in {"CA-R-900", "CA-R-901"},
        )

        self.assertNotIn(copied_row, rows)
        self.assertIn(other_copy, rows)

    def test_real_root_child_inventory_includes_canonical_roles_and_declarations(
        self,
    ) -> None:
        for index, role in enumerate(ROLES, start=1):
            self._write_atom(
                "fixture",
                role,
                f"root-{index}.md",
                atom_id=f"CA-R-{100 + index}",
            )
        self._write_atom(
            "CHILD", "04_requirement", "child.md", atom_id="CA-R-120"
        )

        atoms, scopes, stderr = self._capture()

        self.assertEqual(stderr, "")
        self.assertEqual(
            {row["name"] for row in scopes}, {"fixture", "MAIN", "CHILD"}
        )
        self.assertEqual(len(scopes), len(self.declarations))
        self.assertTrue(
            {
                Path(row["declaration_path"]).relative_to(self.root).as_posix()
                for row in self.declarations.values()
            }
            <= {row["source_path"] for row in atoms}
        )
        role_paths = {
            Path(row["source_path"]).parts[-2]
            for row in atoms
            if Path(row["source_path"]).parts[-2] in ROLES
        }
        self.assertEqual(role_paths, set(ROLES))
        self._assert_inventory_shapes(atoms, scopes)

    def _assert_inventory_shapes(self, atoms, scopes):
        root_source = (
            self.declarations["fixture"]["declaration_path"]
            .relative_to(self.root)
            .as_posix()
        )
        for row in atoms:
            columns = (
                (*ATOM_COLUMNS, "_project_root_header")
                if row["source_path"] == root_source
                else ATOM_COLUMNS
            )
            self.assertEqual(tuple(row), columns)
        self.assertTrue(
            all(
                row["relation_edges_json"] == [] and row["hash"] is None
                for row in atoms
            )
        )
        self.assertTrue(all(tuple(row) == SCOPE_COLUMNS for row in scopes))
        self.assertTrue(
            all(
                row["relation_edges_json"] == [] and row["hash"] is None
                for row in scopes
            )
        )


if __name__ == "__main__":
    unittest.main()
