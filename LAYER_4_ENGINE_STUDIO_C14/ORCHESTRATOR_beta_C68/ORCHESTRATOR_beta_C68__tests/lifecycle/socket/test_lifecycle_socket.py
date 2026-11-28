"""Exercise the real lifecycle worker and kernel through private sockets."""

from hashlib import sha256
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from watchdog.events import (
    DirCreatedEvent,
    DirDeletedEvent,
    DirMovedEvent,
    FileCreatedEvent,
    FileModifiedEvent,
)
from watchdog.utils.dirsnapshot import DirectorySnapshot

from ORCHESTRATOR_beta_C68.watching.watcher_poll import (
    PollComplete,
)
from ...ORCHESTRATOR_beta_C68__tests__shared import (
    project_jobs,
)

from ORCHESTRATOR_beta_C68.ORCHESTRATOR_beta_C68__tests.lifecycle.socket._lifecycle_socket_service_cases import LifecycleSocketServiceCases


class LifecycleSocketTests(LifecycleSocketServiceCases, unittest.TestCase):
    def archive_receipts(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / "control"
        archive = control / "09_archived"
        archive.mkdir(parents=True)
        owned = archive / "owned.md"
        owned.write_text("admitted")
        watcher = self.watcher_jobs(root).watcher
        effects = [
            {
                "target": "control/09_archived",
                "operation": "create",
                "state": "known",
                "evidence": "directory",
            },
            {
                "target": "control/09_archived/owned.md",
                "operation": "create",
                "state": "known",
                "evidence": sha256(owned.read_bytes()).hexdigest(),
            },
        ]
        return watcher, archive, owned, effects

    def archive_poll(self, watcher):
        control = str(watcher.control_root)
        started = time.monotonic_ns()
        watcher._proof.remember_archive_sample(
            control, started, DirectorySnapshot(control)
        )
        self.assertIsNone(watcher._proof.sampled_archive_carriers(started, ()))
        watcher.on_poll_complete(
            PollComplete(control, started=started, clean=True, archive=True)
        )

    def test_admitted_archive_creation_filters_only_its_directory_and_files(
        self,
    ):
        watcher, archive, owned, effects = self.archive_receipts()
        external = archive / "external.md"
        external.write_text("independent")
        before = (object(), 0, 0)
        with patch.object(
            watcher, "capture_epoch", return_value=(before[0], 1, 0)
        ):
            watcher.acknowledge(effects, archive_epoch=before)
            for event in (
                DirCreatedEvent(str(archive)),
                FileCreatedEvent(str(owned)),
                DirCreatedEvent(str(archive)),
                FileCreatedEvent(str(external)),
            ):
                watcher.dispatch(event)
            self.assertEqual(
                [str(external)],
                [change["old_path"] for change in watcher.changes(0.1)],
            )
            self.archive_poll(watcher)
            self.assertEqual([], watcher.changes(0.1))
            watcher.dispatch(DirDeletedEvent(str(archive)))
            watcher.dispatch(
                DirMovedEvent(str(archive), str(archive.parent / "moved"))
            )
            self.assertEqual(
                ["deleted", "moved"],
                [change["event_type"] for change in watcher.changes(0.1)],
            )
            archive.rename(watcher.root / "old")
            archive.mkdir()
            watcher.dispatch(DirCreatedEvent(str(archive)))
            self.assertEqual(
                ["created"],
                [change["event_type"] for change in watcher.changes(0.1)],
            )

    def test_archive_directory_receipts_require_continuous_watcher_coverage(
        self,
    ):
        watcher, archive, _, effects = self.archive_receipts()
        observer = object()
        cases = [
            (None, (observer, 0, 0)),
            ((observer, 0, 0), (observer, 0, 1)),
            ((observer, 0, 0), (object(), 0, 0)),
        ]
        for before, after in cases:
            with (
                self.subTest(before=before, after=after),
                patch.object(watcher, "capture_epoch", return_value=after),
            ):
                watcher.acknowledge(effects, archive_epoch=before)
                watcher.dispatch(DirCreatedEvent(str(archive)))
                self.assertEqual(
                    ["created"],
                    [change["event_type"] for change in watcher.changes(0.1)],
                )

    def test_archive_directory_create_survives_removal_before_first_carrier_event(
        self,
    ):
        watcher, archive, owned, effects = self.archive_receipts()
        before = (object(), 0, 0)
        with patch.object(
            watcher, "capture_epoch", return_value=(before[0], 1, 0)
        ):
            watcher.acknowledge(effects, archive_epoch=before)
            watcher.dispatch(DirCreatedEvent(str(archive)))
            self.assertEqual([], watcher.changes(0.1))
            owned.unlink()
            self.archive_poll(watcher)
            self.assertEqual(
                ["created"],
                [change["event_type"] for change in watcher.changes(0.1)],
            )

    def test_lifecycle_receipts_cover_delayed_watcher_events(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        watcher = self.watcher_jobs(root).watcher
        first, second = root / "first.md", root / "second.md"
        for path in (first, second):
            path.write_text(path.name)
            watcher.acknowledge(
                [
                    {
                        "target": path.name,
                        "operation": "create",
                        "state": "known",
                        "evidence": sha256(path.read_bytes()).hexdigest(),
                    }
                ]
            )
            watcher.queue.put(
                {
                    "old_path": str(path),
                    "new_path": None,
                    "is_directory": False,
                }
            )
        self.assertEqual([], watcher.changes(0.1))
        first.write_text("external edit")
        event = {
            "old_path": str(first),
            "new_path": None,
            "is_directory": False,
        }
        watcher.queue.put(event)
        self.assertEqual([event], watcher.changes(0.1))

    def test_admitted_foreground_directory_creation_preserves_independent_changes(
        self,
    ):
        root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        control = root / "control"
        directory = control / "_SPEC" / "01_draft"
        other_directory = directory.with_name("02_ready")
        for path in (directory, other_directory):
            path.mkdir(parents=True)
        owned, external = directory / "owned.md", directory / "external.md"
        owned.write_text("admitted")
        external.write_text("independent")
        watcher = self.watcher_jobs(root, watch_code=True).watcher
        watcher.acknowledge(
            [
                {
                    "target": str(directory.relative_to(root)),
                    "operation": "create",
                    "state": "known",
                    "evidence": "directory",
                },
                {
                    "target": str(owned.relative_to(root)),
                    "operation": "create",
                    "state": "known",
                    "evidence": sha256(owned.read_bytes()).hexdigest(),
                },
            ]
        )
        for event in (
            DirCreatedEvent(str(directory)),
            FileCreatedEvent(str(owned)),
            FileCreatedEvent(str(external)),
            DirCreatedEvent(str(other_directory)),
        ):
            watcher.dispatch(event)
        self.assertEqual(
            [str(external), str(other_directory)],
            [change["old_path"] for change in watcher.changes(0.1)],
        )

        self._assert_foreground_replacement(watcher, directory, owned)

    def _assert_foreground_replacement(self, watcher, directory, owned):
        owned.write_text("independent replacement")
        watcher.dispatch(FileModifiedEvent(str(owned)))
        watcher.dispatch(DirCreatedEvent(str(directory)))
        self.assertEqual(
            [str(owned), str(directory)],
            [change["old_path"] for change in watcher.changes(0.1)],
        )

        directory.rename(directory.with_name("old"))
        directory.mkdir()
        owned.write_text("admitted")
        watcher.dispatch(DirCreatedEvent(str(directory)))
        self.assertEqual(
            [str(directory)],
            [change["old_path"] for change in watcher.changes(0.1)],
        )

    def test_delayed_foreground_directory_creation_accepts_admitted_carrier_removal(
        self,
    ):
        for admitted in (False, True):
            with self.subTest(admitted=admitted):
                root = Path(
                    self.enterContext(tempfile.TemporaryDirectory())
                ).resolve()
                control = root / "control"
                directory = control / "_SPEC" / "02_ready"
                directory.mkdir(parents=True)
                owned = directory / "owned.md"
                owned.write_text("admitted")
                watcher = self.watcher_jobs(root, watch_code=True).watcher
                carrier = {
                    "target": str(owned.relative_to(root)),
                    "operation": "create",
                    "state": "known",
                    "evidence": sha256(owned.read_bytes()).hexdigest(),
                }
                watcher.acknowledge(
                    [
                        {
                            "target": str(directory.relative_to(root)),
                            "operation": "create",
                            "state": "known",
                            "evidence": "directory",
                        },
                        carrier,
                    ]
                )
                owned.unlink()
                if admitted:
                    watcher.acknowledge([carrier | {"operation": "remove"}])
                watcher.dispatch(DirCreatedEvent(str(directory)))
                expected = [] if admitted else [str(directory)]
                self.assertEqual(
                    expected,
                    [change["old_path"] for change in watcher.changes(0.1)],
                )

    def watcher_jobs(self, root, *, watch_code=False):
        jobs = project_jobs(root, watch_code=watch_code)
        self.addCleanup(jobs.close)
        return jobs
