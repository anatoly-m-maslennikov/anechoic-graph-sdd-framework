"""Check scoped startup checkpoint reconciliation without a database."""
from hashlib import sha256
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .. import native_refresh, WORKERS_beta_C69__shared as worker
from ..startup_inventory import changed_paths, folder_hashes
from .WORKERS_beta_C69__tests__shared import generation_fixture
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import native_carrier_hashes


ENDPOINTS = {"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}


def carrier(number, status="active"):
    return (f"---\natom_family: TKT\natom_id: AN-T-{number}\ncontainer: {{component: C00}}\npriority: 2\ncontext: {{template: task}}\n"
            f"state: {{status: {status}, version: 1, updated_at: '2026-11-22T00:00:00Z'}}\n---\n\n## Summary\n\nTicket {number}.\n")


class IncrementalStartupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.binding, _, _ = generation_fixture(self.tmp.name)
        self.root = Path(self.binding["root"])
        self.control = self.root / self.binding["control_root"]
        self.live = self.control / "__TICKETS"
        self.archive = self.live / "09_archived"
        self.archive.mkdir(parents=True)
        for name, text in (("AN-T-1-task.md", carrier(1)), ("AN-T-2-task.md", carrier(2))):
            (self.live / name).write_text(text)
        (self.archive / "AN-T-8@1-task.md").write_text(carrier(8, "archived"))
        self.roots = [self.archive.relative_to(self.root).as_posix()]
        hashes = native_carrier_hashes(self.binding)
        self.reuse = {"base_generation": "a" * 64, "inputs": {"carrier_schema": "b" * 64},
                      "endpoints": ENDPOINTS, "graph_config": None,
                      "carrier_hashes": hashes, "folder_hashes": folder_hashes(hashes)}
        self.schema = patch.object(native_refresh, "carrier_schema", return_value="b" * 64)
        self.schema.start()
        self.addCleanup(self.schema.stop)

    def capture(self, **options):
        return native_refresh.startup_incremental(self.binding, self.reuse, watcher_guarded=True, **options)

    def test_foreground_unchanged_and_offline_add_edit_move_delete(self):
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, self.capture(foreground=True))
        first = self.live / "AN-T-1-task.md"
        stamp = first.stat()
        first.write_text(first.read_text().replace("Ticket 1.", "Ticket X."))
        os.utime(first, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
        second = self.live / "AN-T-2-task.md"
        moved = self.live / "AN-T-2-moved.md"
        second.rename(moved)
        added = self.live / "AN-T-3-task.md"
        added.write_text(carrier(3))
        result = self.capture(foreground=True)
        paths = {str(Path(parent) / name) for parent, name in result["paths"]}
        self.assertEqual({p.relative_to(self.root).as_posix() for p in (first, second, moved, added)}, paths)
        self.assertEqual({p.relative_to(self.root).as_posix() for p in (first, moved, added)}, set(result["carrier_hashes"]))
        self.assertEqual(3, len(result["snapshot"]["atoms"]))

    def test_archive_unchanged_move_and_delete(self):
        self.assertEqual({"base_generation": "a" * 64, "unchanged": True}, self.capture(archive_roots=self.roots))
        original = self.archive / "AN-T-8@1-task.md"
        moved = self.archive / "AN-T-8@1-moved.md"
        original.rename(moved)
        result = self.capture(archive_roots=self.roots)
        self.assertEqual({original.name, moved.name}, {row[1] for row in result["paths"]})
        self.assertEqual(["Archived"], [row["status_group"] for row in result["snapshot"]["atoms"]])
        moved.unlink()
        self.assertEqual({}, self.capture(archive_roots=self.roots)["carrier_hashes"])

    def test_incompatible_checkpoint_falls_back_and_capture_errors_surface(self):
        self.reuse["folder_hashes"] = {}
        self.assertIsNone(self.capture(foreground=True))
        self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))
        self.reuse["folder_hashes"] = folder_hashes(self.reuse["carrier_hashes"])
        (self.archive / "AN-T-9-task.md").write_text(carrier(9))
        with self.assertRaisesRegex(ValueError, "non-Archived"):
            self.capture(archive_roots=self.roots)

    def test_legacy_carrier_delta_falls_back_without_hiding_parse_errors(self):
        live = self.live / "AN-T-1-task.md"
        live.write_text("---\nidentity: {atom_id: AN-T-1}\ncontext: {container: {component: C00}}\n"
                        "state: {status: active, version: 1}\n---\n\n## Summary\n\nLegacy.\n")
        hashes = native_carrier_hashes(self.binding)
        self.reuse.update(carrier_hashes=hashes, folder_hashes=folder_hashes(hashes))
        live.write_text(live.read_text().replace("Legacy.", "Changed."))
        self.assertIsNone(self.capture(foreground=True))
        live.write_text("---\ninvalid: [\n---\n")
        with self.assertRaises(ValueError):
            self.capture(foreground=True)

    def test_schema_and_large_diff_require_reconciliation(self):
        self.reuse["inputs"].pop("carrier_schema")
        self.assertIsNone(self.capture(foreground=True))
        self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))
        self.reuse["inputs"]["carrier_schema"] = "b" * 64
        many = {f"{self.binding['control_root']}/__TICKETS/AN-T-{i}-task.md": "c" * 64 for i in range(2000, 3025)}
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared.native_carrier_hashes",
                   return_value=many):
            self.assertIsNone(self.capture(foreground=True))
            self.assertEqual({"incompatible": True}, self.capture(archive_roots=self.roots))

    def test_graph_refresh_is_not_guarded_by_foreground_only_watcher(self):
        witness = {"base_generation": "a" * 64, "inputs": {}, "graph_config": {}, "endpoints": {}}
        with patch.object(worker, "refresh", return_value={"base_generation": "a" * 64, "unchanged": True}) as refresh:
            worker._run({"binding": self.binding, "reuse": witness, "foreground": True,
                         "watcher_guarded": True, "incremental": True}, "/unused")
        self.assertFalse(refresh.call_args.args[5].keywords["watcher_guarded"])

    def test_folder_hashes_are_canonical_and_validate_paths(self):
        h = sha256(b"value").hexdigest()
        values = {"b/я.md": h, "b/a.md": h}
        self.assertEqual(folder_hashes(values), folder_hashes(dict(reversed(list(values.items())))))
        self.assertEqual([], changed_paths(values, dict(values), folder_hashes(values)))
        with self.assertRaises(ValueError):
            folder_hashes({"../escape.md": h})
