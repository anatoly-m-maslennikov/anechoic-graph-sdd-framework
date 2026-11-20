"""Verify the disposable legacy-data test checkout."""

from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run_full_test_suite as full


class LegacySuiteFixtureTests(unittest.TestCase):
    def test_fixture_copies_source_and_caches_without_changing_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            for name in (".anechoic_anechoic", ".anechoic_legacy"):
                (root / name).mkdir(parents=True)
                (root / name / "marker").write_text(name)
            (root / ".anechoic_tmp/workbench/extensions").mkdir(parents=True)
            (root / ".anechoic_tmp/workbench/extensions/cache").write_text("cache")
            calls = []

            def run(argv, **kwargs):
                calls.append(argv)
                if argv[1] == "clone":
                    shutil.copytree(root, Path(argv[-1]), ignore=shutil.ignore_patterns(".anechoic_tmp"))
                return SimpleNamespace(stdout=b"abc123\n" if argv[1] == "rev-parse" else b"")

            with patch.object(full.subprocess, "run", side_effect=run):
                with full.legacy_test_fixture(root) as fixture:
                    self.assertEqual((fixture / ".anechoic_anechoic/marker").read_text(), ".anechoic_legacy")
                    self.assertEqual((fixture / ".anechoic_tmp/workbench/extensions/cache").read_text(), "cache")
                    (fixture / ".anechoic_anechoic/marker").write_text("changed")
                self.assertFalse(fixture.exists())
            self.assertIn("--no-hardlinks", next(call for call in calls if call[1] == "clone"))
            self.assertEqual((root / ".anechoic_legacy/marker").read_text(), ".anechoic_legacy")
            self.assertEqual((root / ".anechoic_anechoic/marker").read_text(), ".anechoic_anechoic")

    def test_rejects_dirty_source_before_clone(self):
        with patch.object(full.subprocess, "run", return_value=SimpleNamespace(stdout=b" M tracked\n")):
            with self.assertRaisesRegex(OSError, "clean tracked source"):
                with full.legacy_test_fixture(Path("/source")):
                    self.fail("dirty source was accepted")

    def test_rejects_cache_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            for name in (".anechoic_anechoic", ".anechoic_legacy", ".anechoic_tmp/workbench"):
                (root / name).mkdir(parents=True)
            (root / ".anechoic_tmp/workbench/extensions").symlink_to("outside")

            def run(argv, **kwargs):
                if argv[1] == "clone":
                    shutil.copytree(root, Path(argv[-1]), ignore=shutil.ignore_patterns(".anechoic_tmp"))
                return SimpleNamespace(stdout=b"abc123\n" if argv[1] == "rev-parse" else b"")

            with patch.object(full.subprocess, "run", side_effect=run):
                with self.assertRaisesRegex(OSError, "test cache is a symbolic link"):
                    with full.legacy_test_fixture(root):
                        self.fail("cache symlink was accepted")


if __name__ == "__main__":
    unittest.main()
