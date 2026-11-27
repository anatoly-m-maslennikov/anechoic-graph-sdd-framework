"""Exercise the release's 48-hour scratch retention policy."""

import errno
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__shared import (
    run_local_release,
)
from LAYER_2_LOCAL_RELEASE_C63.release_cleanup_tmp import prune_temporary_files
from LAYER_2_LOCAL_RELEASE_C63.LAYER_2_LOCAL_RELEASE_C63__tests.\
    LAYER_2_LOCAL_RELEASE_C63__tests__shared \
    import SimpleReleaseFixture  # fmt: skip


class TemporaryCleanupTests(unittest.TestCase):
    def test_removes_only_entries_strictly_older_than_cutoff(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            temporary = root / ".anechoic_tmp"
            stale = temporary / "run/old.log"
            stale.parent.mkdir(parents=True)
            stale.touch()
            outside = root / "outside"
            outside.mkdir()
            marker = outside / "keep"
            marker.touch()
            link = temporary / "external-link"
            link.symlink_to(outside, target_is_directory=True)
            for path in (stale, stale.parent, marker, link):
                os.utime(path, (10, 10), follow_symlinks=False)
            keep = [
                temporary / name
                for name in (
                    "exactly-48h.log",
                    "fresh.log",
                    "local_release_installation/installation.lock",
                    "atom_lifecycle/write.lock",
                    "cache/uv/cached",
                    "workbench/playwright-browsers/chrome",
                    "workbench/extensions/duckpgq.duckdb_extension",
                    "rmed-base-revise/resumable.json",
                )
            ]
            for path, modified in zip(
                keep, (11, 12, 10, 10, 10, 10, 10, 10), strict=True
            ):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                os.utime(path, (modified, modified))
            with patch(
                "LAYER_2_LOCAL_RELEASE_C63.release_cleanup_tmp.time.time_ns",
                return_value=(48 * 3600 + 11) * 10**9,
            ):
                self.assertEqual((3, []), prune_temporary_files(root))
            self.assertFalse(stale.parent.exists())
            self.assertFalse(link.is_symlink())
            self.assertTrue(marker.is_file())
            for path in keep:
                self.assertTrue(path.is_file(), path)

    def test_permission_error_keeps_other_entries_eligible(self):
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            temporary = root / ".anechoic_tmp"
            temporary.mkdir()
            for name in ("blocked.log", "expired.log"):
                path = temporary / name
                path.touch()
                os.utime(path, (10, 10))
            unlink = os.unlink

            def deny_one(name, *, dir_fd):
                if name == "blocked.log":
                    raise PermissionError(errno.EACCES, "Permission denied")
                unlink(name, dir_fd=dir_fd)

            with patch(
                "LAYER_2_LOCAL_RELEASE_C63.release_cleanup_tmp.os.unlink",
                side_effect=deny_one,
            ):
                self.assertEqual(
                    (1, ["blocked.log: Permission denied"]),
                    prune_temporary_files(root),
                )
            self.assertTrue((temporary / "blocked.log").is_file())
            self.assertFalse((temporary / "expired.log").exists())


class FinalTemporaryCleanupTests(SimpleReleaseFixture, unittest.TestCase):
    def test_final_release_expires_scratch_and_records_result(self):
        stale = self.root / ".anechoic_tmp/old-run.log"
        stale.parent.mkdir(exist_ok=True)
        stale.touch()
        os.utime(stale, (10, 10))
        runner, _ = self._runner()
        result = run_local_release(
            self.root, run_id="tmp-expiry", runner=runner
        )
        self.assertEqual("completed", result["outcome"], result)
        self.assertFalse(stale.exists())
        self.assertIn(
            "Removed 1 temporary paths older than 48 hours.",
            (self.root / result["receipt_path"]).read_text(),
        )
