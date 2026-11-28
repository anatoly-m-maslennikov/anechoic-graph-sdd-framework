"""Authority-root discovery is independent of declared Scope membership."""

from __future__ import annotations

from .source_discovery_incremental_cases import SourceDiscoveryIncrementalCases
from .source_discovery_asset_cases import SourceDiscoveryAssetCases

import json  # noqa: F401
import unittest
from unittest.mock import patch

from ..reading import test_source_reader as fixtures
from ...schema.content_schema_fixture import SUMMARY_CLAIM, python_claim_body  # noqa: F401
from IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IWE_CONSOLE_BACKEND.FEATURE_IWE_CONSOLE_BACKEND__tests.schema.workbench_schema_fixture import (
    generate_asset,  # noqa: F401
)


class SourceDiscoveryTests(
    SourceDiscoveryIncrementalCases,
    SourceDiscoveryAssetCases,
    unittest.TestCase,
):
    def setUp(self):
        self.fixture = fixtures.SourceReaderTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root, self.control = self.fixture.root, self.fixture.control
        self.reader = self.fixture.reader

    def source(
        self,
        relative: str,
        atom_id: str,
        *,
        status="Active",
        form="Declaration",
        body=None,
    ):
        template = self.fixture._write_atom(
            "MAIN",
            "04_requirement",
            "seed.md",
            atom_id=atom_id,
            status=status,
            form=form,
            body=body or "## Summary\n\nA source outside the Scope tree.\n",
        )
        raw = template.read_bytes()
        template.unlink()
        path = self.control / relative
        path = path.with_name(f"{atom_id}-{path.name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    def test_root_discovery_includes_loose_and_unregistered_sources_only_inside_boundary(
        self,
    ):
        current = self.source(
            "retired-owner/04_requirement/current.md", "CA-R-780"
        )
        draft = self.source(
            "loose/draft/proposal.md", "CA-R-781", status="Draft"
        )
        copied = self.source("installed-copy/custom/record.md", "CA-R-782")
        additional = [
            self.source("retired-owner/archive/old.md", "CA-R-783"),
            self.source("loose/old.md", "CA-R-785", status="Archived"),
        ]
        generated = [
            self.source("_projection/copy.md", "CA-R-784"),
            self.source(
                (
                    "000_ANECHOIC_framework/SUPERLAYER_1_METHODOLOGY_SOURCES/"
                    "copy.md"
                ),
                "CA-R-787",
            ),
            self.source(
                "000_ANECHOIC_framework/applicable_methodology/copy.md",
                "CA-R-788",
            ),
        ]
        outside = self.root / "CA-R-786-outside.md"
        outside.write_bytes(
            current.read_bytes().replace(b"CA-R-780", b"CA-R-786")
        )
        atoms, scopes, diagnostics = self.fixture._capture()
        self.assertEqual("", diagnostics)
        paths = {row["source_path"] for row in atoms}
        for path in (current, draft, copied, *additional):
            self.assertIn(path.relative_to(self.root).as_posix(), paths)
        for path in generated:
            self.assertNotIn(path.relative_to(self.root).as_posix(), paths)
        self.assertNotIn(outside.relative_to(self.root).as_posix(), paths)
        self.assertEqual(
            {"fixture", "MAIN", "CHILD"}, {row["name"] for row in scopes}
        )
        self._assert_draft_discovered(atoms)

    def _assert_draft_discovered(self, atoms):
        self.assertEqual(
            "Draft",
            next(row for row in atoms if row["id"] == "CA-R-781")[
                "status_group"
            ],
        )

    def test_duplicate_loads_both_carriers_and_keeps_survivor_after_delete(
        self,
    ):
        copies = [
            self.source(f"{directory}/copy.md", "CA-R-802")
            for directory in ("a", "z")
        ]
        atoms, _, _ = self.fixture._capture()
        selected = [row for row in atoms if row["ref"] == "CA-R-802"]
        self.assertEqual(2, len(selected))
        winner = min(copies)
        later = max(copies)
        winner.unlink()
        with patch.object(
            self.reader,
            "_inventory_paths",
            side_effect=AssertionError("unexpected full scan"),
        ):
            atoms, _ = self.reader.capture(
                [
                    {
                        "operation": "remove",
                        "old_path": winner.relative_to(self.root).as_posix(),
                        "new_path": None,
                    }
                ]
            )
        selected = [row for row in atoms if row["ref"] == "CA-R-802"]
        self.assertEqual(
            [later.relative_to(self.root).as_posix()],
            [row["source_path"] for row in selected],
        )
        self.assertIsNone(
            self.reader.capture_delta[winner.relative_to(self.root).as_posix()]
        )
        self.assertIsNotNone(
            self.reader.capture_delta[later.relative_to(self.root).as_posix()]
        )


if __name__ == "__main__":
    unittest.main()
