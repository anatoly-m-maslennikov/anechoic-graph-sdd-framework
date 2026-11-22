import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from .. import prune_private_tmp as cleanup


class PrivateScratchCleanupTests(unittest.TestCase):
    def test_expires_only_old_owned_scratch_outside_open_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            project = root / "project"
            now = time.time()
            old = now - cleanup.RETENTION_SECONDS - 60
            stale, unmarked, fresh, active, mounted = (
                root / name for name in ("stale", "unmarked", "fresh", "active", "mounted")
            )
            for path in (stale, unmarked, fresh, active, mounted, project):
                path.mkdir(mode=0o700)
                if path not in (unmarked, project):
                    cleanup.mark(path, root, project)
                if path in (stale, active, mounted):
                    os.utime(path / cleanup.MARKER, (old, old))
                os.utime(path, (old, old))
            (root / "link").symlink_to(stale, target_is_directory=True)
            with patch.object(cleanup, "protected_paths", return_value=([mounted / "output"], [active / "file"])):
                cleanup.prune(root, project, now)
            self.assertFalse(stale.exists())
            for path in (unmarked, fresh, active, mounted, project):
                self.assertTrue(path.is_dir())
            self.assertTrue((root / "link").is_symlink())
