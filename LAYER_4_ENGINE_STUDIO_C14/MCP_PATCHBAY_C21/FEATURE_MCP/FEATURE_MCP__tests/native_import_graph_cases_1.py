"""Exercise the Import Graph through the native Workbench routes."""

import os
from unittest.mock import patch


from . import test_native_query_stdio as fixture
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import ReadContext


_CARRIER_1 = """---
atom_family: TKT
atom_id: AN-T-010
container:
  component: C00
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---
## Summary

Existing task
"""

_CARRIER_2 = """---
atom_family: TKT
atom_id: AN-T-010
structure:
  container:
    component: C00
  priority: 2
context:
  template: task
  label: Task
state:
  status: active
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---
## Summary

Existing task
"""

class ImportGraphCases1:
    def _check_revision(self, owner, store, draft):
        revised = owner.lifecycle('atom_lifecycle_update', {
            'sourceCurrent': {'ref_id': draft['atom_id'], 'version': 1},
            'changes': {'body': '## Summary\n\nIncremental lifecycle refresh.\n\nRevised.\n'},
        })
        self.assertFalse(revised['errors'], revised)
        revision = revised['savedDraft']
        published = owner.lifecycle('atom_lifecycle_promote_draft', {
            'target': {'ref_id': revision['ref_id'], 'version': revision['version']},
            'targetStatus': 'backlog',
        })
        self.assertFalse(published['errors'], published)
        active, archived = draft['atom_id'], draft['atom_id'] + '@1'
        with store._lock:
            self.assertEqual(store._connection.execute(
                'SELECT reference, "header.state.version", "header.state.status" '
                'FROM atoms WHERE reference IN (?, ?, ?) ORDER BY "header.state.version"',
                [active, archived, revision['ref_id']],
            ).fetchall(), [(archived, 1, 'archived'), (active, 2, 'backlog')])

    async def test_lifecycle_writes_refresh_atoms_without_full_projection(self):
        unrelated = self._source(f"{fixture.CONTROL}/001_TICKETS/TASKS/AN-T-010-TASK--existing-task.md", _CARRIER_1)
        gateway = await self._gateway(enabled=False)
        owner = gateway._native_query
        store = owner._owner()
        with owner._interface_lock, patch.object(owner, '_project', side_effect=AssertionError('full projection')):
            created = owner.lifecycle('atom_lifecycle_create_draft', {'newAtom': {
                'template': 'task', 'label': 'Task', 'container': {'component': 'C00'},
                'body': '## Summary\n\nIncremental lifecycle refresh.\n',
            }})
            self.assertFalse(created['errors'], created)
            draft = created['savedDraft']
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT reference FROM atoms WHERE reference = ?', [draft['ref_id']]
                ).fetchall(), [(draft['ref_id'],)])

            reads = []
            read = ReadContext.read

            def record_read(reader, path, **kwargs):
                reads.append(path)
                return read(reader, path, **kwargs)

            with patch.object(ReadContext, 'read', record_read):
                promoted = owner.lifecycle('atom_lifecycle_promote_draft', {
                    'target': {'ref_id': draft['ref_id'], 'version': draft['version']},
                    'targetStatus': 'backlog',
                })
            self.assertNotIn(unrelated, reads)
            self.assertFalse(promoted['errors'], promoted)
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT reference FROM atoms WHERE reference IN (?, ?) ORDER BY reference',
                    [draft['ref_id'], draft['atom_id']],
                ).fetchall(), [(draft['atom_id'],)])

            self._check_revision(owner, store, draft)


    async def test_promotion_detects_unseen_duplicate_with_restored_mtime(self):
        carrier = _CARRIER_2
        self._source(f"{fixture.CONTROL}/001_TICKETS/TASKS/AN-T-010-TASK--existing-task.md", carrier)
        duplicate = self._source(
            f"{fixture.CONTROL}/001_TICKETS/TASKS/09_archived/unrelated.md",
            carrier.replace('AN-T-010', 'AN-T-999').replace('status: active', 'status: archived')
                   .replace('version: 1', 'version: 2'),
        )
        gateway = await self._gateway(enabled=False)
        owner = gateway._native_query
        with owner._interface_lock:
            result = owner.lifecycle('atom_lifecycle_update', {
                'sourceCurrent': {'ref_id': 'AN-T-010', 'version': 1},
                'changes': {'body': '## Summary\n\nExisting task\n\nRevised.\n'},
            })
            self.assertFalse(result['errors'], result)
            self.assertIn('savedDraft', result, result)
            draft = result['savedDraft']
            before = duplicate.stat()
            duplicate.write_text(duplicate.read_text().replace('AN-T-999', 'AN-T-010'))
            os.utime(duplicate, ns=(before.st_atime_ns, before.st_mtime_ns))
            self.assertEqual(duplicate.stat().st_size, before.st_size)
            self.assertEqual(duplicate.stat().st_mtime_ns, before.st_mtime_ns)
            promoted = owner.lifecycle('atom_lifecycle_promote_draft', {
                'target': {'ref_id': draft['ref_id'], 'version': draft['version']},
                'targetStatus': 'backlog',
            })
            self.assertEqual(promoted['outcome'], 'needs_input', promoted)
            self.assertIn('already has a non-Draft revision',
                          promoted['requested_input']['target']['error'])
            self.assertFalse(promoted['effects'])
            self.assertTrue(duplicate.exists())


    def _exercise_file_changes(self, owner, store, control, source, refresh, record_read, scoped_inventory):
        with (owner._interface_lock, patch.object(ReadContext, "read", record_read),
              patch.object(ReadContext, "inventory", scoped_inventory)):
            self._write(source.relative_to(control), "AN-T-010", "active", 1)
            refresh([(None, source), (None, source)], expected=[source], files=[source])
            refresh([(None, source)], expected=[], files=[source])
            self._write(source.relative_to(control), "AN-T-010", "active", 2)
            refresh([(None, source)], expected=[source], files=[source])
            temporary = source.with_suffix(".tmp")
            temporary.write_bytes(source.read_bytes().replace(b"version: 2", b"version: 3"))
            temporary.replace(source)
            refresh([(temporary, source)], expected=[source], files=[source])
            with store._lock:
                self.assertEqual(store._connection.execute(
                    'SELECT "header.state.version" FROM atoms WHERE reference = ?', ['AN-T-010'],
                ).fetchall(), [(3,)])
            renamed = source.rename(source.with_name("AN-T-010-TASK--renamed.md"))
            refresh([(source, renamed)], expected=[renamed], files=[renamed])
            folder = control / "001_TICKETS/TASKS/container"
            added = folder / "nested/AN-T-011-TASK--nested.md"
            self._write(added.relative_to(control), "AN-T-011", "active", 1)
            refresh([(None, folder), (None, added)], expected=[added], files=[renamed, added])
            moved = renamed.rename(folder / renamed.name)
            refresh([(renamed, moved)], expected=[moved], files=[moved, added])
            destination = folder.rename(folder.with_name("renamed-folder"))
            new_moved, new_added = [destination / path.relative_to(folder) for path in (moved, added)]
            refresh([(folder, destination), (added, new_added)], expected=[new_moved, new_added],
                    files=[new_moved, new_added])
            new_moved.unlink()
            refresh([(new_moved, None)], expected=[], files=[new_added])
            new_added.unlink()
            new_added.parent.rmdir()
            destination.rmdir()
            refresh([(destination, None)], expected=[], files=[])



    async def test_workbench_file_and_directory_changes_read_only_affected_carriers(self):
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

        def refresh(operations, *, expected, files):
            batch = [{"old_path": old.relative_to(self.root).as_posix() if old else None,
                      "new_path": new.relative_to(self.root).as_posix() if new else None}
                     for old, new in operations]
            reads.clear()
            self.assertEqual(owner._watch_atom_changes(store, batch, set()), set())
            self.assertCountEqual(reads, expected)
            with store._lock:
                rows = store._connection.execute(
                    "SELECT relative_path, filename FROM atoms WHERE reference IN ('AN-T-010', 'AN-T-011')"
                ).fetchall()
            self.assertCountEqual([self.root / folder / name for folder, name in rows], files)

        self._exercise_file_changes(owner, store, control, source, refresh, record_read, scoped_inventory)
