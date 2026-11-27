"""Watcher callback translation is deterministic before service batch handling."""

from pathlib import Path
from unittest.mock import NonCallableMock
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import SourceWatcher  # noqa: E402


class _Observer:
    def __init__(self) -> None:
        self.handler = None
        self.path = None
        self.recursive = None
        self.started = False
        self.stopped = False
        self.joined = False
        self.schedules = []
        self.unscheduled = []
        self.pending_changes = None

    def schedule(self, handler, path: str, recursive: bool) -> str:
        if not recursive:
            assert self.pending_changes is not None
            assert not self.pending_changes(0), "change published before directory watch registration"
        self.schedules.append((path, recursive))
        self.handler, self.path, self.recursive = handler, path, recursive
        return path

    def unschedule(self, watch: str) -> None:
        self.unscheduled.append(watch)

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def join(self) -> None:
        self.joined = True


class SourceWatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.control = self.root / ".anechoic_example"
        self.control.mkdir()
        self.observer = _Observer()
        self.watcher = SourceWatcher(
            self.root, self.control, observer_factory=lambda: self.observer,
        )
        self.observer.pending_changes = self.watcher.changes
        self.watcher.start()

    def event(self, source: Path, *, destination: Path | None = None, directory: bool = False):
        return NonCallableMock(
            spec_set=['src_path', 'dest_path', 'is_directory'],
            src_path=str(source),
            dest_path=str(destination) if destination is not None else None,
            is_directory=directory,
        )

    def test_root_file_watch_is_nonrecursive(self) -> None:
        observer = _Observer()
        watcher = SourceWatcher(self.root, self.control, observer_factory=lambda: observer, watch_root_files=True)
        observer.pending_changes = watcher.changes
        watcher.start()
        self.addCleanup(watcher.close)
        self.assertIn((str(self.root.absolute()), False), observer.schedules)
        observer.handler.on_modified(self.event(self.root / 'AN-S-1-SPEC-PROJECT_GOAL--goal.md'))
        observer.handler.on_modified(self.event(self.root / 'outside' / 'nested.md'))
        self.assertEqual([{'operation': 'update', 'old_path': None,
                           'new_path': 'AN-S-1-SPEC-PROJECT_GOAL--goal.md'}], watcher.changes(0))

    def test_file_callbacks_keep_selected_repository_relative_paths(self) -> None:
        path = self.control / "04_requirement/CA-R-1.md"
        self.observer.handler.on_created(self.event(path))
        self.observer.handler.on_modified(self.event(path))
        self.observer.handler.on_deleted(self.event(path))

        self.assertEqual([
            {"operation": "create", "old_path": None, "new_path": ".anechoic_example/04_requirement/CA-R-1.md"},
            {"operation": "update", "old_path": None, "new_path": ".anechoic_example/04_requirement/CA-R-1.md"},
            {"operation": "remove", "old_path": ".anechoic_example/04_requirement/CA-R-1.md", "new_path": None},
        ], self.watcher.changes(0))

    def test_moves_keep_native_boundary_and_parent_meaning(self) -> None:
        old = self.control / "04_requirement/CA-R-1.md"
        renamed = self.control / "04_requirement/CA-R-2.md"
        moved = self.control / "05_method/CA-R-2.md"
        outside = self.root / "outside.md"
        self.observer.handler.on_moved(self.event(old, destination=renamed))
        self.observer.handler.on_moved(self.event(renamed, destination=moved))
        self.observer.handler.on_moved(self.event(outside, destination=old))
        self.observer.handler.on_moved(self.event(moved, destination=outside))
        self.observer.handler.on_moved(self.event(outside, destination=self.root / "elsewhere.md"))

        self.assertEqual([
            {"operation": "rename", "old_path": ".anechoic_example/04_requirement/CA-R-1.md", "new_path": ".anechoic_example/04_requirement/CA-R-2.md"},
            {"operation": "move", "old_path": ".anechoic_example/04_requirement/CA-R-2.md", "new_path": ".anechoic_example/05_method/CA-R-2.md"},
            {"operation": "create", "old_path": None, "new_path": ".anechoic_example/04_requirement/CA-R-1.md"},
            {"operation": "remove", "old_path": ".anechoic_example/05_method/CA-R-2.md", "new_path": None},
        ], self.watcher.changes(0))

    def test_directory_create_move_remove_are_kept_but_modify_is_ignored(self) -> None:
        directory = self.control / "04_requirement"
        other = self.control / "nested/05_method"
        self.observer.handler.on_created(self.event(directory, directory=True))
        self.observer.handler.on_modified(self.event(directory, directory=True))
        self.observer.handler.on_moved(self.event(directory, destination=other, directory=True))
        self.observer.handler.on_deleted(self.event(other, directory=True))

        self.assertEqual([
            {"operation": "create", "old_path": None, "new_path": ".anechoic_example/04_requirement"},
            {"operation": "move", "old_path": ".anechoic_example/04_requirement", "new_path": ".anechoic_example/nested/05_method"},
            {"operation": "remove", "old_path": ".anechoic_example/nested/05_method", "new_path": None},
        ], self.watcher.changes(0))

    def test_directory_reported_as_file_gets_a_child_watch_and_removal_cleans_it_up(self) -> None:
        directory = self.control / "new"
        directory.mkdir()
        self.observer.handler.on_created(self.event(directory))

        self.assertIn((str(directory.resolve()), False), self.observer.schedules)
        self.observer.handler.on_deleted(self.event(directory))
        self.assertIn(str(directory.resolve()), self.observer.unscheduled)

    def test_native_directory_events_watch_the_created_and_moved_subtrees(self) -> None:
        directory = self.control / "new"
        directory.mkdir()
        self.observer.handler.on_created(self.event(directory, directory=True))
        self.watcher.changes(0)
        destination = self.control / "renamed"
        directory.rename(destination)
        self.observer.handler.on_moved(self.event(directory, destination=destination, directory=True))
        self.assertEqual([
            (str(self.control), True),
            (str(directory.resolve(strict=False)), False),
            (str(destination.resolve()), False),
        ], self.observer.schedules)
        self.assertEqual([str(directory.resolve())], self.observer.unscheduled)

    def test_native_large_directory_move_watches_destination_before_move_record(self) -> None:
        source = self.control / "source" / "batch"
        source.mkdir(parents=True)
        for index in range(500):
            (source / f"CA-R-{index:03d}.md").touch()
        destination = self.control / "target" / "batch"
        destination.parent.mkdir()
        source.rename(destination)

        self.observer.handler.on_moved(self.event(source, destination=destination, directory=True))

        self.assertIn((str(destination.resolve()), False), self.observer.schedules)
        self.assertEqual([
            {
                "operation": "move",
                "old_path": ".anechoic_example/source/batch",
                "new_path": ".anechoic_example/target/batch",
            },
        ], self.watcher.changes(0))

    def test_native_directory_move_outside_is_removed_without_outside_traversal(self) -> None:
        source = self.control / "source"
        source.mkdir()
        destination = self.root / "outside" / "source"
        destination.parent.mkdir()
        source.rename(destination)

        with mock.patch.object(Path, "rglob", side_effect=AssertionError("outside traversal")):
            self.observer.handler.on_moved(self.event(
                source, destination=destination, directory=True,
            ))

        self.assertEqual([(str(self.control), True)], self.observer.schedules)
        self.assertEqual([
            {
                "operation": "remove",
                "old_path": ".anechoic_example/source",
                "new_path": None,
            },
        ], self.watcher.changes(0))

    def test_moved_in_directory_gets_a_child_watch_before_move_is_recorded(self) -> None:
        source = self.root / "outside"
        destination = self.control / "moved"
        source.mkdir()
        source.rename(destination)

        self.observer.handler.on_moved(self.event(source, destination=destination))

        self.assertIn((str(destination.resolve()), False), self.observer.schedules)
        self.assertEqual([
            {"operation": "create", "old_path": None, "new_path": ".anechoic_example/moved"},
        ], self.watcher.changes(0))

    def test_close_stops_the_native_observer(self) -> None:
        self.watcher.close()
        self.assertTrue(self.observer.stopped)
        self.assertTrue(self.observer.joined)

    def test_filtered_root_schedules_and_registers_new_directories_before_events(self) -> None:
        self.watcher.close()
        excluded = self.root / "excluded"
        excluded.mkdir()
        (self.root / "linked").symlink_to(self.control, target_is_directory=True)
        self.observer = _Observer()
        self.watcher = SourceWatcher(
            self.root, self.root, observer_factory=lambda: self.observer,
            exclude_directory=lambda path: path == "excluded" or path.startswith("excluded/"),
        )
        self.observer.pending_changes = self.watcher.changes
        self.watcher.start()
        self.assertEqual({(str(self.root), False), (str(self.control), True)}, set(self.observer.schedules))

        new = self.root / "new"
        new.mkdir()
        self.observer.handler.on_created(self.event(new, directory=True))
        self.assertIn((str(new), True), self.observer.schedules)
        self.assertEqual("new", self.watcher.changes(0)[0]["new_path"])
        self.observer.handler.on_created(self.event(excluded, directory=True))
        self.assertNotIn((str(excluded), True), self.observer.schedules)
        self.watcher.changes(0)
        moved = self.root / "moved"
        new.rename(moved)
        self.observer.handler.on_moved(self.event(new, destination=moved, directory=True))
        self.assertIn((str(moved), True), self.observer.schedules)
        self.assertEqual("rename", self.watcher.changes(0)[0]["operation"])
        self.observer.handler.on_created(self.event(self.root / "linked", directory=True))
        self.assertNotIn((str(self.root / "linked"), True), self.observer.schedules)
        self.watcher.changes(0)
        self.observer.handler.on_created(self.event(self.root / "file.py"))
        self.assertEqual("file.py", self.watcher.changes(0)[0]["new_path"])

    def test_positive_timeout_collects_one_fixed_event_window(self) -> None:
        event = self.event(self.control / "first.md")
        self.observer.handler.on_created(event)

        def add_update() -> None:
            time.sleep(0.01)
            self.observer.handler.on_modified(event)

        worker = threading.Thread(target=add_update)
        worker.start()
        batch = self.watcher.changes(0.05)
        worker.join(timeout=1)

        self.assertEqual(["create", "update"], [event["operation"] for event in batch])

    def test_control_root_outside_project_is_refused(self) -> None:
        with self.assertRaisesRegex(ValueError, "inside the selected repository"):
            SourceWatcher(self.root, self.root.parent / "other")


if __name__ == "__main__":
    unittest.main()
