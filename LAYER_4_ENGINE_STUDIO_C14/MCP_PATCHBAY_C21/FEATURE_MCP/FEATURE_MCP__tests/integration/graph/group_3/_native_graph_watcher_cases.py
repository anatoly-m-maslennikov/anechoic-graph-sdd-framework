"""Exercise the Import Graph through the native Workbench routes."""

from unittest.mock import patch


from ...query.group_1 import test_native_query_stdio as fixture
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    ReadContext,
)


class NativeGraphWatcherCases:
    def _exercise_file_changes(
        self,
        owner,
        store,
        control,
        source,
        refresh,
        record_read,
        scoped_inventory,
    ):
        with (
            owner._interface_lock,
            patch.object(ReadContext, "read", record_read),
            patch.object(ReadContext, "inventory", scoped_inventory),
        ):
            self._write(source.relative_to(control), "AN-T-010", "active", 1)
            refresh(
                [(None, source), (None, source)],
                expected=[source],
                files=[source],
            )
            refresh([(None, source)], expected=[], files=[source])
            self._write(source.relative_to(control), "AN-T-010", "active", 2)
            refresh([(None, source)], expected=[source], files=[source])
            temporary = source.with_suffix(".tmp")
            temporary.write_bytes(
                source.read_bytes().replace(b"version: 2", b"version: 3")
            )
            temporary.replace(source)
            refresh([(temporary, source)], expected=[source], files=[source])
            self._check_watched_version(store)
            renamed = source.rename(
                source.with_name("AN-T-010-TASK--renamed.md")
            )
            refresh([(source, renamed)], expected=[renamed], files=[renamed])
            self._exercise_directory_changes(control, renamed, refresh)

    def _exercise_directory_changes(self, control, renamed, refresh):
        folder = control / "001_TICKETS/TASKS/container"
        added = folder / "nested/AN-T-011-TASK--nested.md"
        self._write(added.relative_to(control), "AN-T-011", "active", 1)
        refresh(
            [(None, folder), (None, added)],
            expected=[added],
            files=[renamed, added],
        )
        moved = renamed.rename(folder / renamed.name)
        refresh([(renamed, moved)], expected=[moved], files=[moved, added])
        destination = folder.rename(folder.with_name("renamed-folder"))
        new_moved, new_added = [
            destination / path.relative_to(folder) for path in (moved, added)
        ]
        refresh(
            [(folder, destination), (added, new_added)],
            expected=[new_moved, new_added],
            files=[new_moved, new_added],
        )
        new_moved.unlink()
        refresh([(new_moved, None)], expected=[], files=[new_added])
        new_added.unlink()
        new_added.parent.rmdir()
        destination.rmdir()
        refresh([(destination, None)], expected=[], files=[])

    def _check_watched_version(self, store):
        with store._lock:
            self.assertEqual(
                store._connection.execute(
                    (
                        'SELECT "header.state.version" FROM atoms WHERE '
                        "reference = ?"
                    ),
                    ["AN-T-010"],
                ).fetchall(),
                [(3,)],
            )

    async def test_workbench_file_and_directory_changes_read_only_affected_carriers(
        self,
    ):
        gateway = await self._gateway(enabled=False)
        owner = gateway._native_query
        store = owner._owner()
        control = self.root / fixture.CONTROL
        source = control / "001_TICKETS/TASKS/AN-T-010-TASK--created.md"
        read, inventory = ReadContext.read, ReadContext.inventory
        reads = []

        def record_read(reader, path, **kwargs):
            raw = read(reader, path, **kwargs)
            if raw is not None:
                reads.append(path)
            return raw

        def scoped_inventory(reader, path, **kwargs):
            self.assertNotEqual(path, control)
            return inventory(reader, path, **kwargs)

        refresh = self._watch_refresh(owner, store, reads)

        self._exercise_file_changes(
            owner,
            store,
            control,
            source,
            refresh,
            record_read,
            scoped_inventory,
        )

    def _watch_refresh(self, owner, store, reads):
        def refresh(operations, *, expected, files):
            batch = [
                {
                    "old_path": old.relative_to(self.root).as_posix()
                    if old
                    else None,
                    "new_path": new.relative_to(self.root).as_posix()
                    if new
                    else None,
                }
                for old, new in operations
            ]
            reads.clear()
            self.assertEqual(
                owner._watch_atom_changes(store, batch, set()), set()
            )
            self.assertCountEqual(reads, expected)
            with store._lock:
                rows = store._connection.execute(
                    (
                        "SELECT relative_path, filename FROM atoms WHERE "
                        "reference IN ('AN-T-010', 'AN-T-011')"
                    )
                ).fetchall()
            self.assertCountEqual(
                [self.root / folder / name for folder, name in rows], files
            )

        return refresh
