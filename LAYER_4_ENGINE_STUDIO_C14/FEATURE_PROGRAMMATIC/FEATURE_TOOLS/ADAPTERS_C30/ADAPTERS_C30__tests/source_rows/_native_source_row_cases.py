"""Native capture inventory and Model-input cases."""

from hashlib import sha256
from pathlib import PurePosixPath
import os
from unittest.mock import NonCallableMock, patch

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext,
    native_carrier_hashes,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
    revalidate_native,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.model_capture import (
    model_inputs,
)


class NativeSourceRowCases:
    def test_hash_inventory_tracks_content_and_deletion(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        path = self.write("AN-T-8--hash.md", "AN-T-8", "active", 1)
        ignored = self.control / "000_ANECHOIC_framework" / "ignored.md"
        ignored.parent.mkdir()
        ignored.write_text("not a carrier")
        relative = path.relative_to(self.root).as_posix()
        before = native_carrier_hashes(binding)
        self.assertEqual(
            sha256(path.read_bytes()).hexdigest(), before[relative]
        )
        self.assertEqual(
            {self.manifest.relative_to(self.root).as_posix(), relative},
            set(before),
        )
        stat = path.stat()
        path.write_bytes(path.read_bytes().replace(b"Example", b"Changed"))
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns))
        after = native_carrier_hashes(binding)
        self.assertNotEqual(before[relative], after[relative])
        path.unlink()
        self.assertNotIn(relative, native_carrier_hashes(binding))

    def test_raw_hashes_include_root_goal_and_reject_inventory_race(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        goal = self.root / "AN-S-02-SPEC-PROJECT_GOAL--goal.md"
        goal.write_bytes(b"not parsed by hashing")
        self.assertEqual(
            sha256(goal.read_bytes()).hexdigest(),
            native_carrier_hashes(binding)[goal.name],
        )
        original = ReadContext.read

        def read_and_change(reader, path, **kwargs):
            raw = original(reader, path, **kwargs)
            if path == goal and kwargs.get("remember", True):
                (self.control / "new.md").write_text("new")
            return raw

        with patch.object(ReadContext, "read", read_and_change):
            with self.assertRaisesRegex(ValueError, "changed during capture"):
                native_carrier_hashes(binding)

    def test_current_draft_archived_and_header_containment(self):
        self.write("__TKT/TASKS/AN-T-09--task.md", "AN-T-09", "active", 2)
        self.write(
            "__TKT/TASKS/draft/AN-T-09@3-draft--task.md", "AN-T-09", "draft", 3
        )
        self.write(
            "__TKT/ASSETS/AN-T-10--asset.md",
            "AN-T-10",
            "active",
            1,
            {"atom": "AN-T-09"},
        )
        self.write(
            "__TKT/TASKS/AN-T-11@1-draft--linked.md",
            "AN-T-11",
            "draft",
            1,
            {"atom": "AN-T-09"},
        )
        self.write("archived/AN-S-001@2--old.md", "AN-S-001", "archived", 2)
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        rows = {row["_exact_ref"]: row for row in result.atoms}
        self.assertEqual("AN-T-09", rows["AN-T-09@2"]["ref"])
        self.assertEqual("Current", rows["AN-T-09@2"]["status_group"])
        self.assertEqual("AN-T-09@3-draft", rows["AN-T-09@3-draft"]["ref"])
        self.assertEqual("Draft", rows["AN-T-11@1-draft"]["status_group"])
        self.assertEqual("AN-S-001@2", rows["AN-S-001@2"]["ref"])
        asset = next(
            edge
            for edge in result.containment
            if edge["source_ref"] == "AN-T-10"
        )
        self.assertEqual(
            ("Atom", "AN-T-09"), (asset["target_kind"], asset["target_ref"])
        )
        self.assertIn(b"Example", rows["AN-T-10@1"]["_content_bytes"])

    def test_structure_issue_uses_classification_and_candidate_location(self):
        alias = self.control / "AN-S-2-SPEC-OTHER--alias.md"
        header = self._structure_header()
        alias.write_text(
            "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n"
        )
        off_path = (
            self.control / "_QA/AN-S-3-SPEC-COMPONENT_MANIFEST--invalid.md"
        )
        off_path.parent.mkdir()
        off_path.write_text("---\ninvalid: [\n---\n")
        capture = capture_native(self.selection)
        selected = NonCallableMock(
            spec_set=[
                "root",
                "control_root",
                "manifest_path",
                "project_prefix",
            ],
            root=self.root,
            control_root=self.control,
            manifest_path=self.root / "other",
            project_prefix="AN",
        )
        capture_view = NonCallableMock(
            spec_set=[
                "atoms",
                "ingestion_issues",
                "errors",
                "classified_templates",
            ],
            atoms=[],
            ingestion_issues=capture.ingestion_issues,
            errors=capture.errors,
            classified_templates=capture.classified_templates,
        )
        result = model_inputs(selected, capture_view, include_spec_rows=True)
        assert not result["structure_issues"]
        assert result["structure_alias_issues"] == (
            {
                "relative_path": alias.relative_to(self.root).as_posix(),
                "template": "component_manifest",
            },
        )
        self._check_structure_revalidation(alias, header, capture)

    def _structure_header(self):
        return {
            "atom_family": "SPEC",
            "atom_id": "AN-S-2",
            "container": {"component": "C00"},
            "tier": 1,
            "context": {"template": "component_manifest", "lens": "SPEC"},
            "state": {
                "status": "active",
                "version": 0,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }

    def _check_structure_revalidation(self, alias, header, capture):
        header["state"]["version"] = 1
        alias.write_text(
            "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n"
        )
        updated = capture_native(
            self.selection,
            previous=capture,
            paths={PurePosixPath(alias.relative_to(self.root).as_posix())},
        )
        assert (
            alias.relative_to(self.root).as_posix()
            not in updated.classified_templates
        )
        assert alias.relative_to(self.root).as_posix() not in updated.errors

    def test_root_manifest_and_goal_capture_and_incremental_revalidation(self):
        self.manifest = self.manifest.rename(self.root / self.manifest.name)
        self.selection.manifest_path = self.manifest
        goal = self.root / "AN-S-02-SPEC-PROJECT_GOAL--goal.md"
        header = {
            "atom_family": "SPEC",
            "atom_id": "AN-S-02",
            "container": {"component": "C00"},
            "tier": -1,
            "context": {"template": "project_goal", "lens": "SPEC"},
            "state": {
                "status": "active",
                "version": 1,
                "updated_at": "2026-11-19T00:00:00Z",
            },
        }
        text = "---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\n"
        goal.write_text(text + "Goal\n")
        (self.root / "AN-S-03-SPEC--unrelated.md").write_text(
            "Unrelated Markdown"
        )
        first = capture_native(self.selection)
        self.assertEqual({}, first.errors)
        self.assertEqual(
            {self.manifest.name, goal.name},
            {row["source_path"] for row in first.atoms},
        )

        goal.write_text(text + "Updated goal\n")
        updated = revalidate_native(self.selection, first)
        row = next(
            row for row in updated.atoms if row["source_path"] == goal.name
        )
        self.assertIn(b"Updated goal", row["_content_bytes"])
        goal.unlink()
        remaining = revalidate_native(self.selection, updated)
        self.assertEqual(
            [self.manifest.name],
            [row["source_path"] for row in remaining.atoms],
        )
