"""Check safe mechanical creation of a native Project Manifest."""

import ast
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from RUNTIME_SETUP__tests.RUNTIME_SETUP__tests__shared import ROOT

from RUNTIME_SETUP__shared import initialize_project


class ProjectInitTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        (self.root / "existing.txt").write_text("keep", encoding="utf-8")

    def initialize(self, **kwargs):
        return initialize_project(ROOT, self.root, kwargs.pop("name", "My Project"),
                                  kwargs.pop("prefix", "MP"),
                                  workbench_storage=kwargs.pop("workbench_storage", "memory"),
                                  journal_storage=kwargs.pop("journal_storage", "duckdb"), **kwargs)

    def manifest_fields(self, control):
        manifest = self.root / "MP-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
        text = manifest.read_text(encoding="utf-8")
        self.assertIn("atom_id: MP-S-1\n", text)
        self.assertIn("  template: project_manifest\n", text)
        self.assertIn("  status: active\n", text)
        claim = ast.parse(text.split("```python\n", 1)[1].split("\n```", 1)[0])
        call = claim.body[-1].value
        project = next(kw.value for kw in call.keywords if kw.arg == "instance")
        return {kw.arg: ast.literal_eval(kw.value) for kw in project.keywords}

    def test_manifest_contains_project_identity_storage_and_layout(self):
        control = self.initialize()
        self.assertEqual(self.root / ".anechoic_my project", control)
        self.assertEqual([], list(control.iterdir()))
        fields = self.manifest_fields(control)
        self.assertEqual("My Project", fields["name"])
        self.assertEqual("MP", fields["prefix"])
        self.assertEqual({"workbench": {"storage": "memory"}, "journal": {"storage": "duckdb"}},
                         fields["parameters"]["runtime"])
        self.assertEqual({"0": ".", "1": "01_TIER_1_ARCHITECTURE", "2+": "_{lens}/{sublenses}"},
                         fields["parameters"]["project"]["folder_layout"]["active_spec_by_tier"])
        manifest = self.root / "MP-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
        self.assertIn(
            "        parameters={\n"
            "            'runtime': {\n"
            "                'workbench': {'storage': 'memory'},\n"
            "                'journal': {'storage': 'duckdb'},\n",
            manifest.read_text(encoding="utf-8"),
        )
        self.assertEqual("keep", (self.root / "existing.txt").read_text(encoding="utf-8"))

    def test_existing_candidate_and_symlink_are_preserved(self):
        candidate = self.root / "_anechoic_other"
        candidate.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            self.initialize()
        self.assertTrue(candidate.is_symlink())
        candidate.unlink()
        control = self.initialize()
        manifest = self.root / "MP-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
        before = manifest.read_bytes()
        with self.assertRaises(FileExistsError):
            self.initialize()
        self.assertEqual(before, manifest.read_bytes())

    def test_existing_root_manifest_is_preserved(self):
        manifest = self.root / "OTHER-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
        manifest.write_text("preserve")
        with self.assertRaises(FileExistsError):
            self.initialize()
        self.assertEqual("preserve", manifest.read_text())
        self.assertFalse((self.root / ".anechoic_my project").exists())

    def test_disk_and_files_modes_are_persisted(self):
        control = self.initialize(workbench_storage="disk", journal_storage="files")
        self.assertEqual({"workbench": {"storage": "disk"}, "journal": {"storage": "files"}},
                         self.manifest_fields(control)["parameters"]["runtime"])

    def test_fsync_failure_cleans_owned_temporary_and_empty_directory(self):
        with patch.object(os, "fsync", side_effect=OSError("disk error")):
            with self.assertRaisesRegex(OSError, "disk error"):
                self.initialize()
        self.assertEqual(["existing.txt"], [entry.name for entry in self.root.iterdir()])

    def test_publish_collision_preserves_existing_file(self):
        real_link = os.link

        def collide(source, destination, *, src_dir_fd, dst_dir_fd, follow_symlinks):
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600, dir_fd=dst_dir_fd)
            with os.fdopen(fd, "w") as stream:
                stream.write("preserve")
            return real_link(source, destination, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd,
                             follow_symlinks=follow_symlinks)

        with patch.object(os, "link", side_effect=collide):
            with self.assertRaises(FileExistsError):
                self.initialize()
        self.assertFalse((self.root / ".anechoic_my project").exists())
        manifest = self.root / "MP-S-1-SPEC-PROJECT_MANIFEST--declare-project.md"
        self.assertEqual("preserve", manifest.read_text())

    def test_invalid_inputs_do_not_create_control(self):
        for changes in ({"name": "../unsafe"}, {"name": "bad```name"}, {"name": "runtime"}, {"prefix": "M-P"},
                        {"workbench_storage": "other"}, {"journal_storage": "other"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.initialize(**changes)
        self.assertEqual(["existing.txt"], [entry.name for entry in self.root.iterdir()])

    def test_symlinked_project_root_is_refused(self):
        link = self.root.parent / (self.root.name + "-link")
        link.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(link.unlink)
        with self.assertRaises(ValueError):
            initialize_project(ROOT, link, "Example", "EX", workbench_storage="disk", journal_storage="files")


if __name__ == "__main__":
    unittest.main()
