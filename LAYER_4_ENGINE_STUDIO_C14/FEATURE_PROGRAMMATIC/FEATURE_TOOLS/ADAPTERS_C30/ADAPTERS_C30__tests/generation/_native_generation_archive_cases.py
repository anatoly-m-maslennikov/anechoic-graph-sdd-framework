"""Native generation test cases."""

from contextlib import redirect_stderr
from hashlib import sha256
from io import StringIO
import json
import os
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    ReadContext,
    native_carrier_hashes,
    prepare_generation_snapshot,
)  # fmt: skip


class NativeGenerationArchiveCases:
    def test_foreground_archive_versions_use_names_without_reading_files(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        archive = self._archive_names_fixture()
        versions, reads = {}, []
        read = ReadContext.read

        def record_read(reader, path, **options):
            reads.append(path)
            return read(reader, path, **options)

        with (
            patch.object(ReadContext, "read", record_read),
            patch(
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "native_snapshot_cli._graph_config",
                return_value={},
            ),
        ):
            _, finish = prepare_generation_snapshot(
                binding, archive_stage="foreground", archive_versions=versions
            )
            self.assertEqual(
                5,
                len(
                    finish(
                        {
                            "CONTAINED_BY": [
                                {"inverse_alias": "CONTAINS"},
                                False,
                            ],
                            "CONTAINS": [{}, True],
                        }
                    )
                ),
            )
        self.assertEqual({"AN-S-3": 7, "AN-T-5": 9}, versions)
        self.assertFalse(any(path.is_relative_to(archive) for path in reads))

    def _archive_names_fixture(self):
        self.write("AN-S-3@4--off-path.md", "AN-S-3", "archived", 4)
        archive = self.control / "09_archived"
        (archive / "nested").mkdir(parents=True)
        for name in (
            "AN-S-3@2--broken.md",
            "nested/AN-S-3@7--broken.md",
            "nested/AN-T-5@9--broken.md",
            "AN-S-8@0--bad.md",
            "AN-S-8@9223372036854775808--bad.md",
            "OTHER-S-2@8--bad.md",
            "AN-R-2@8--bad.md",
            "nonsense.md",
        ):
            (archive / name).write_bytes(b"\xff invalid YAML")
        (archive / "AN-S-9@99--link.md").symlink_to(
            archive / "AN-S-3@2--broken.md"
        )
        (archive / "linked-dir").symlink_to(
            archive / "nested", target_is_directory=True
        )
        return archive

    def _assert_foreground_reads(
        self, archived, installed, off_path, roots, reads, stats
    ):
        self.assertEqual(
            [archived.parent.relative_to(self.root).as_posix()], roots
        )
        self.assertIn(off_path, reads)
        self.assertNotIn(archived, reads)
        self.assertNotIn(archived, stats)
        self.assertNotIn(installed, stats)

    def test_archive_stage_validates_roots_and_reports_non_archived_carriers(
        self,
    ):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        path = self.write(
            "09_archived/AN-S-2--active.md", "AN-S-2", "active", 1
        )
        relative = path.relative_to(self.root).as_posix()
        with self.assertRaisesRegex(
            ValueError, "outside the selected native archive trees"
        ):
            prepare_generation_snapshot(
                binding, archive_stage="archive", archive_roots=["09_archived"]
            )
        _, finish = prepare_generation_snapshot(
            binding,
            archive_stage="archive",
            include_hashes=True,
            archive_roots=[path.parent.relative_to(self.root).as_posix()],
        )
        snapshot, hashes = finish(
            {
                "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                "CONTAINS": [{}, True],
            }
        )
        self.assertEqual([], snapshot["atoms"])
        (issue,) = snapshot["ingestion_issues"]
        self.assertEqual(
            (relative, "AN-S-2@1"), (issue["relative_path"], issue["atom_ref"])
        )
        self.assertIn("non-Archived Atom", issue["message"])
        self.assertEqual(
            {relative: sha256(path.read_bytes()).hexdigest()}, hashes
        )

    def \
   test_scoped_hashes_exclude_deferred_archives_and_keep_off_path_revisions(
        self,
    ):  # fmt: skip
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        live = self.write("AN-S-2--current.md", "AN-S-2", "active", 1)
        off_path = self.write("AN-S-3@1--off-path.md", "AN-S-3", "archived", 1)
        archived = self.write(
            "09_archived/AN-S-4@1--archived.md", "AN-S-4", "archived", 1
        )
        roots = [archived.parent.relative_to(self.root).as_posix()]
        with patch.object(ReadContext, "currentness") as currentness:
            foreground = native_carrier_hashes(
                binding, foreground=True, watcher_guarded=True
            )
            background = native_carrier_hashes(
                binding, archive_roots=roots, watcher_guarded=True
            )
        currentness.assert_not_called()
        self.assertEqual(
            {self.manifest, live, off_path},
            {self.root / path for path in foreground},
        )
        self.assertEqual({archived}, {self.root / path for path in background})

    def test_foreground_timing_reports_scans_only_when_enabled(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        current = self.write("AN-S-2--current.md", "AN-S-2", "active", 1)
        archived = self.write(
            "09_archived/AN-S-3@1--archived.md", "AN-S-3", "archived", 1
        )
        archive_roots = [archived.parent.relative_to(self.root).as_posix()]
        disabled, enabled = StringIO(), StringIO()
        with (
            patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "0"}),
            redirect_stderr(disabled),
        ):
            expected = native_carrier_hashes(binding, foreground=True)
        self.assertEqual("", disabled.getvalue())
        with (
            patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}),
            redirect_stderr(enabled),
            patch(
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "native_snapshot_cli._graph_config",
                return_value={},
            ),
        ):
            self.assertEqual(
                expected, native_carrier_hashes(binding, foreground=True)
            )
            native_carrier_hashes(binding, archive_roots=archive_roots)
            prepare_generation_snapshot(binding, archive_stage="foreground")
        self._check_timing_records(enabled, current)

    def _check_timing_records(self, enabled, current):
        prefix = "ANECHOIC_STARTUP_TIMING "
        lines = enabled.getvalue().splitlines()
        self.assertTrue(all(line.startswith(prefix) for line in lines), lines)
        records = [json.loads(line.removeprefix(prefix)) for line in lines]
        self.assertEqual(
            [
                ("scan_started", "foreground_hashes"),
                ("scan_metrics", "foreground_hashes"),
                ("scan_started", "foreground_capture"),
                ("non_archived_load_started", "foreground_capture"),
                ("scan_metrics", "foreground_capture"),
            ],
            [(row["phase"], row["mode"]) for row in records],
        )
        for row in records:
            self.assertIs(type(row["timestamp_ns"]), int)
            self.assertGreater(row["timestamp_ns"], 0)
            if row["phase"] == "scan_metrics":
                self.assertEqual(2, row["carrier_count"])
                self.assertEqual(
                    self.manifest.stat().st_size + current.stat().st_size,
                    row["bytes_read"],
                )
                for field in (
                    "census_ns",
                    "guarded_read_ns",
                    "stream_ns",
                    "sha256_ns",
                ):
                    self.assertIs(type(row[field]), int)
                    self.assertGreaterEqual(row[field], 0)
                self.assertLessEqual(row["stream_ns"], row["guarded_read_ns"])
        self.assertNotIn(str(self.root), enabled.getvalue())

    def test_managed_snapshot_can_delegate_final_currentness_to_watcher(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        endpoints = {
            "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
            "CONTAINS": [{}, True],
        }
        with (
            patch(
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "native_snapshot_cli._graph_config",
                return_value={},
            ),
            patch.object(ReadContext, "currentness") as currentness,
        ):
            _, finish = prepare_generation_snapshot(
                binding, watcher_guarded=True
            )
            self.assertTrue(finish(endpoints)["atoms"])
        currentness.assert_not_called()
