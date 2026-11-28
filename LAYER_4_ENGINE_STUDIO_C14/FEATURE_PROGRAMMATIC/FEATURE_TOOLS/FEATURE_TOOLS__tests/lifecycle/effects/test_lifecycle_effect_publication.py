"""A watcher must see the final inode after the staging link is removed."""

from pathlib import Path
import os
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[3]
ROOT = TOOLS.parents[2]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.ATOM_LIFECYCLE__shared import (  # noqa: E402
    effects_module as effects,
)


class PublicationTest(unittest.TestCase):
    def test_watcher_cannot_observe_staged_hard_link(self):
        base = ROOT / ".anechoic_tmp" / "effect-publication-test"
        base.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            path = Path(directory) / "CA-R-1-TEST.md"
            lock = threading.RLock()
            attempted, observed = threading.Event(), []
            original_link = os.link
            workers = []

            class Reader:
                def lifecycle_file_effect(self):
                    return lock

                def lifecycle_read(self, target, *, descriptor=None):
                    return target.read_bytes()

                def lifecycle_changed(self, old, new):
                    observed.append(("notification", new.stat().st_nlink))

            def link_then_watch(*args, **kwargs):
                original_link(*args, **kwargs)

                def watch():
                    attempted.set()
                    with lock:
                        observed.append(("watcher", path.stat().st_nlink))

                worker = threading.Thread(target=watch)
                worker.start()
                workers.append(worker)
                self.assertTrue(attempted.wait(1))
                self.assertEqual([], observed)

            with (
                patch.object(effects, "_reader", return_value=Reader()),
                patch.object(effects.os, "link", side_effect=link_then_watch),
            ):
                result = effects.create(ROOT, path, b"content")
            for worker in workers:
                worker.join(1)
                self.assertFalse(worker.is_alive())
            self.assertFalse(result.errors, result.errors)
            self.assertEqual(
                {("watcher", 1), ("notification", 1)}, set(observed)
            )


if __name__ == "__main__":
    unittest.main()
