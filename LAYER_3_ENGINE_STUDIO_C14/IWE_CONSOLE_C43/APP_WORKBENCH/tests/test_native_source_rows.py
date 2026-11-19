from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

import yaml

APP_ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(APP_ROOT), str(APP_ROOT.parent / "FEATURE_PROGRAMMATIC" / "FEATURE_TOOLS")]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.native_source_rows import capture_native  # noqa: E402


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

    def test_invalid_and_duplicate_carriers_are_reported(self):
        self.write("one/AN-S-1--one.md", "AN-S-1", "active", 1)
        self.write("two/AN-S-1--two.md", "AN-S-1", "active", 2)
        self.write("AN-T-2--bad.md", "AN-T-2", "bogus", 1)
        result = capture_native(self.selection)
        self.assertEqual(2, len(result.errors))
        self.assertTrue(any("Duplicate" in error for error in result.errors.values()))
        self.assertTrue(any("status" in error for error in result.errors.values()))

    def test_manifest_drift_refuses_capture(self):
        self.manifest.write_text("changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Manifest changed"):
            capture_native(self.selection)

    def test_archive_rejects_a_draft_marker_and_wrong_tree(self):
        self.write("archived/AN-S-2@1-draft--withdrawn.md", "AN-S-2", "archived", 1)
        self.write("__TKT/ASSETS/AN-S-3--wrong-tree.md", "AN-S-3", "active", 1)
        reports = capture_native(self.selection).errors
        self.assertEqual(2, len(reports))
        self.assertTrue(any("Filename marker" in error for error in reports.values()))
        self.assertTrue(any("logical tree" in error for error in reports.values()))


if __name__ == "__main__":
    unittest.main()
