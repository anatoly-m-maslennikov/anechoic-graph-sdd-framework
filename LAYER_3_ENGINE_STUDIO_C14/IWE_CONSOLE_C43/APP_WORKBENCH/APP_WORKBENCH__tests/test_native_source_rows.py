from hashlib import sha256
from pathlib import Path, PurePosixPath
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

APP_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(APP_ROOT), str(APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS")]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native, revalidate_native  # noqa: E402


class NativeCaptureTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.control = self.root / ".anechoic_test"
        self.control.mkdir()
        self.manifest = self.write("AN-S-001-PROJECT_MANIFEST--manifest.md", "AN-S-001", "active", 1)
        self.selection = SimpleNamespace(root=self.root, control_root=self.control,
                                         manifest_path=self.manifest, project_prefix="AN",
                                         manifest_sha256=sha256(self.manifest.read_bytes()).hexdigest())

    def write(self, relative, atom_id, status, version, container=None):
        if "-T-" in atom_id and not relative.startswith("__TKT/"):
            relative = "__TKT/TASKS/" + relative
        path = self.control / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": atom_id}, "context": {"container": container or {"component": "C0"}},
                  "state": {"status": status, "version": version, "updated_at": "2026-11-19T00:00:00Z"}}
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n", encoding="utf-8")
        return path

    def test_current_draft_archived_and_header_containment(self):
        self.write("__TKT/TASKS/AN-T-09--task.md", "AN-T-09", "active", 2)
        self.write("__TKT/TASKS/draft/AN-T-09@3-draft--task.md", "AN-T-09", "draft", 3)
        self.write("__TKT/ASSETS/AN-T-10--asset.md", "AN-T-10", "active", 1, {"atom": "AN-T-09"})
        self.write("__TKT/TASKS/AN-T-11@1-draft--linked.md", "AN-T-11", "draft", 1, {"atom": "AN-T-09"})
        self.write("archived/AN-S-001@2--old.md", "AN-S-001", "archived", 2)
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        rows = {row["_exact_ref"]: row for row in result.atoms}
        self.assertEqual("AN-T-09", rows["AN-T-09@2"]["ref"])
        self.assertEqual("Current", rows["AN-T-09@2"]["status_group"])
        self.assertEqual("AN-T-09@3-draft", rows["AN-T-09@3-draft"]["ref"])
        self.assertEqual("Draft", rows["AN-T-11@1-draft"]["status_group"])
        self.assertEqual("AN-S-001@2", rows["AN-S-001@2"]["ref"])
        asset = next(edge for edge in result.containment if edge["source_ref"] == "AN-T-10")
        self.assertEqual(("Atom", "AN-T-09"), (asset["target_kind"], asset["target_ref"]))
        self.assertIn(b"Example", rows["AN-T-10@1"]["_content_bytes"])

    def test_canonical_header_controls_identity_and_preserves_authored_metadata(self):
        path = self.control / "__TKT" / "arbitrary-name.md"
        path.parent.mkdir(parents=True)
        header = {"atom_family": "SPEC", "atom_id": "AN-S-20",
                  "structure": {"container": {"component": "C0"}, "tier": 3},
                  "context": {"lens": "example"},
                  "state": {"status": "active", "version": 1,
                            "updated_at": "2026-11-19T00:00:00Z"}}
        path.write_text("---\n" + yaml.safe_dump(header) + "---\n\n## Summary\n\nExample\n")
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        row = next(row for row in result.atoms if row["id"] == "AN-S-20")
        self.assertEqual(header, row["header_json"])
        self.assertEqual(3, row["tier"])
        self.assertEqual("AN-S-20", row["ref"])
        self.assertEqual("C0", next(edge for edge in result.containment
                                     if edge["source_ref"] == "AN-S-20")["target_ref"])

        duplicate = self.control / "elsewhere.md"
        duplicate.write_bytes(path.read_bytes())
        self.assertTrue(any("Duplicate" in error for error in capture_native(self.selection).errors.values()))

    def test_invalid_and_duplicate_carriers_are_reported(self):
        self.write("one/AN-S-1--one.md", "AN-S-1", "active", 1)
        self.write("two/AN-S-1--two.md", "AN-S-1", "active", 2)
        self.write("AN-T-2--bad.md", "AN-T-2", "bogus", 1)
        result = capture_native(self.selection)
        self.assertEqual(2, len(result.errors))
        self.assertTrue(any("Duplicate" in error for error in result.errors.values()))
        self.assertTrue(any("status" in error for error in result.errors.values()))

    def test_installed_methodology_copies_are_excluded(self):
        active = self.write("AN-S-2--definition.md", "AN-S-2", "active", 1)
        copy = self.control / "000_ANECHOIC_framework/sources" / active.name
        copy.parent.mkdir(parents=True)
        copy.write_bytes(active.read_bytes())
        result = capture_native(self.selection)
        self.assertEqual({}, result.errors)
        self.assertEqual({"AN-S-001@1", "AN-S-2@1"}, {row["_exact_ref"] for row in result.atoms})

    def test_incremental_capture_reads_changes_and_matches_full_after_move(self):
        old = self.write("AN-S-2--old.md", "AN-S-2", "active", 1)
        untouched = self.write("AN-S-3--untouched.md", "AN-S-3", "active", 1)
        previous = capture_native(self.selection)
        new = old.with_name("AN-S-2--new.md")
        old.rename(new)
        changed = {PurePosixPath(path.relative_to(self.root).as_posix()) for path in (old, new)}
        from VALIDATE_ATOMS.validate_atoms_workers.read_io import ReadContext
        read = ReadContext.read
        with patch.object(ReadContext, "read", autospec=True, side_effect=read) as reads:
            result = capture_native(self.selection, previous=previous, paths=changed)
        self.assertNotIn(untouched, [call.args[1] for call in reads.call_args_list])
        self.assertEqual(capture_native(self.selection), result)

    def test_incremental_duplicate_and_repair(self):
        original = self.write("one/AN-S-2--one.md", "AN-S-2", "active", 1)
        duplicate = self.control / "two" / original.name
        duplicate.parent.mkdir()
        previous = capture_native(self.selection)
        duplicate.write_bytes(original.read_bytes())
        changed = {PurePosixPath(duplicate.relative_to(self.root).as_posix())}
        result = capture_native(self.selection, previous=previous, paths=changed)
        self.assertTrue(any("Duplicate" in error for error in result.errors.values()))
        duplicate.unlink()
        repaired = capture_native(self.selection, previous=result, paths=changed)
        self.assertEqual(capture_native(self.selection), repaired)
        self.assertEqual(repaired, revalidate_native(self.selection, result))

    def test_manifest_drift_refuses_capture(self):
        self.manifest.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Manifest changed"):
            capture_native(self.selection)

    def test_revalidation_refuses_new_carrier_between_inventory_passes(self):
        previous = capture_native(self.selection)

        def capture_then_add(*args, **kwargs):
            captured = capture_native(*args, **kwargs)
            self.write("new/AN-S-2--added.md", "AN-S-2", "active", 1)
            return captured

        with patch(f"{capture_native.__module__}.capture_native", side_effect=capture_then_add):
            with self.assertRaisesRegex(ValueError, "carriers changed during capture"):
                revalidate_native(self.selection, previous)

    def test_archive_rejects_a_draft_marker_and_wrong_tree(self):
        self.write("archived/AN-S-2@1-draft--withdrawn.md", "AN-S-2", "archived", 1)
        self.write("__TKT/ASSETS/AN-S-3--wrong-tree.md", "AN-S-3", "active", 1)
        reports = capture_native(self.selection).errors
        self.assertEqual(2, len(reports))
        self.assertTrue(any("Filename marker" in error for error in reports.values()))
        self.assertTrue(any("logical tree" in error for error in reports.values()))


if __name__ == "__main__":
    unittest.main()
