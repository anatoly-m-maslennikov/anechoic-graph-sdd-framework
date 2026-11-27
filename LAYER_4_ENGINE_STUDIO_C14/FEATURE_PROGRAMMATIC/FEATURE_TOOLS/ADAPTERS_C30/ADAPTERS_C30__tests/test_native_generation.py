from contextlib import redirect_stderr
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
from time import monotonic
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext, capture_native, capture_ticket_delta, native_carrier_hashes, prepare_generation_snapshot, status_domains,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)


class NativeGenerationTests(NativeCaptureFixture, unittest.TestCase):
    def test_generation_capture_uses_admitted_status_domains(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        domains = status_domains({})
        domains["C"] = domains["P"] = domains["C"] | {"reviewed"}
        self.write("__PROJECT_CONFIG/AN-C-1--valid.md", "AN-C-1", "reviewed", 1)
        unknown = self.write("__PROJECT_CONFIG/AN-C-2--unknown.md", "AN-C-2", "unknown", 1)
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={}):
            _, finish = prepare_generation_snapshot(binding)
            result = finish({"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}, domains)
        row = next(row for row in result["atoms"] if row["reference"] == "AN-C-1")
        self.assertEqual(("reviewed", "Current"), (row["status"], row["status_group"]))
        self.assertIn(unknown.relative_to(self.root).as_posix(),
                      {issue["relative_path"] for issue in result["ingestion_issues"]})

    def test_atom_projection_uses_authored_header_context(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_generation_snapshot import _atoms

        base = {"ref": "AN-S-2", "_exact_ref": "AN-S-2@1", "status_group": "Current",
                "source_path": "spec.md", "_summary_title": "Example", "status": "active", "version": 1}
        context = {"container": {"component": "C42"}, "tier": 2, "template": "DES"}
        rows = _atoms([base | {"header_json": {"atom_family": "SPEC", "atom_id": "AN-S-2",
                                                "container": context["container"], "tier": 2,
                                                "context": {"template": "DES"}, "state": {"status": "active",
                                                "version": 1, "updated_at": "2026-11-19T00:00:00Z"}}},
                       base | {"ref": "AN-S-3", "header_json": {"context": {"container": {"atom": "AN-S-2"}}}}])
        self.assertEqual(("C42", 2, "DES"), tuple(rows[0][key] for key in ("container_component", "tier", "template")))
        self.assertEqual((None, None, None), tuple(rows[1][key] for key in ("container_component", "tier", "template")))

    def test_staged_capture_reads_archives_without_reopening_foreground_carriers(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        current = self.write("AN-S-2--current.md", "AN-S-2", "active", 2)
        draft = self.write("01_draft/AN-S-2@3-draft--draft.md", "AN-S-2", "draft", 3)
        off_path = self.write("AN-S-3@1--off-path.md", "AN-S-3", "archived", 1)
        archived = self.write("09_archived/AN-S-4@1--archived.md", "AN-S-4", "archived", 1,
                              {"atom": "AN-S-2"})
        installed = self.write("000_ANECHOIC_framework/09_archived/AN-S-5@1--installed.md",
                               "AN-S-5", "archived", 1)
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
        reads, stats = [], []
        read, lstat = ReadContext.read, Path.lstat

        def record_read(reader, path, **options):
            reads.append(path)
            return read(reader, path, **options)

        def record_lstat(path):
            stats.append(path)
            return lstat(path)

        with (patch.object(ReadContext, "read", record_read), patch.object(Path, "lstat", record_lstat),
              patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config",
                    return_value={})):
            _, finish = prepare_generation_snapshot(binding, archive_stage="foreground")
            foreground, hashes, roots, off_path_snapshot, off_path_hashes = finish(endpoints)
            self.assertEqual({"AN-S-001", "AN-S-2", "AN-S-2@3-draft"},
                             {row["reference"] for row in foreground["atoms"]})
            self.assertEqual({self.manifest, current, draft}, {self.root / path for path in hashes})
            self.assertEqual(["AN-S-3@1"], [row["reference"] for row in off_path_snapshot["atoms"]])
            self.assertEqual({off_path}, {self.root / path for path in off_path_hashes})
            self._assert_foreground_reads(archived, installed, off_path, roots, reads, stats)

            reads.clear()
            graph, finish = prepare_generation_snapshot(
                binding, include_hashes=True, archive_stage="archive", archive_roots=roots,
            )
            archive_snapshot, archive_hashes = finish(endpoints)
            self.assertIsNone(graph)
            self.assertEqual({archived, self.manifest}, set(reads))
            self.assertEqual({archived}, {self.root / path for path in archive_hashes})
            self.assertEqual(["AN-S-4@1"], [row["reference"] for row in archive_snapshot["atoms"]])
            self.assertIn({"source_kind": "Atom", "source_ref": "AN-S-2", "target_kind": "Atom",
                           "target_ref": "AN-S-4@1", "relation_type": "CONTAINS", "derived": True},
                          archive_snapshot["relations"])

    def test_foreground_archive_versions_use_names_without_reading_files(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        self.write("AN-S-3@4--off-path.md", "AN-S-3", "archived", 4)
        archive = self.control / "09_archived"
        (archive / "nested").mkdir(parents=True)
        for name in ("AN-S-3@2--broken.md", "nested/AN-S-3@7--broken.md",
                     "nested/AN-T-5@9--broken.md", "AN-S-8@0--bad.md",
                     "AN-S-8@9223372036854775808--bad.md", "OTHER-S-2@8--bad.md",
                     "AN-R-2@8--bad.md", "nonsense.md"):
            (archive / name).write_bytes(b"\xff invalid YAML")
        (archive / "AN-S-9@99--link.md").symlink_to(archive / "AN-S-3@2--broken.md")
        (archive / "linked-dir").symlink_to(archive / "nested", target_is_directory=True)
        versions, reads = {}, []
        read = ReadContext.read

        def record_read(reader, path, **options):
            reads.append(path)
            return read(reader, path, **options)

        with (patch.object(ReadContext, "read", record_read),
              patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={})):
            _, finish = prepare_generation_snapshot(binding, archive_stage="foreground", archive_versions=versions)
            self.assertEqual(5, len(finish({"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                                            "CONTAINS": [{}, True]})))
        self.assertEqual({"AN-S-3": 7, "AN-T-5": 9}, versions)
        self.assertFalse(any(path.is_relative_to(archive) for path in reads))

    def _assert_foreground_reads(self, archived, installed, off_path, roots, reads, stats):
        self.assertEqual([archived.parent.relative_to(self.root).as_posix()], roots)
        self.assertIn(off_path, reads)
        self.assertNotIn(archived, reads)
        self.assertNotIn(archived, stats)
        self.assertNotIn(installed, stats)

    def test_archive_stage_validates_roots_and_reports_non_archived_carriers(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        path = self.write("09_archived/AN-S-2--active.md", "AN-S-2", "active", 1)
        relative = path.relative_to(self.root).as_posix()
        with self.assertRaisesRegex(ValueError, "outside the selected native archive trees"):
            prepare_generation_snapshot(binding, archive_stage="archive", archive_roots=["09_archived"])
        _, finish = prepare_generation_snapshot(binding, archive_stage="archive", include_hashes=True,
                                                archive_roots=[path.parent.relative_to(self.root).as_posix()])
        snapshot, hashes = finish({"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]})
        self.assertEqual([], snapshot["atoms"])
        issue, = snapshot["ingestion_issues"]
        self.assertEqual((relative, "AN-S-2@1"), (issue["relative_path"], issue["atom_ref"]))
        self.assertIn("non-Archived Atom", issue["message"])
        self.assertEqual({relative: sha256(path.read_bytes()).hexdigest()}, hashes)

    def test_scoped_hashes_exclude_deferred_archives_and_keep_off_path_revisions(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        live = self.write("AN-S-2--current.md", "AN-S-2", "active", 1)
        off_path = self.write("AN-S-3@1--off-path.md", "AN-S-3", "archived", 1)
        archived = self.write("09_archived/AN-S-4@1--archived.md", "AN-S-4", "archived", 1)
        roots = [archived.parent.relative_to(self.root).as_posix()]
        with patch.object(ReadContext, "currentness") as currentness:
            foreground = native_carrier_hashes(binding, foreground=True, watcher_guarded=True)
            background = native_carrier_hashes(binding, archive_roots=roots, watcher_guarded=True)
        currentness.assert_not_called()
        self.assertEqual({self.manifest, live, off_path}, {self.root / path for path in foreground})
        self.assertEqual({archived}, {self.root / path for path in background})

    def test_foreground_timing_reports_scans_only_when_enabled(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        current = self.write("AN-S-2--current.md", "AN-S-2", "active", 1)
        archived = self.write("09_archived/AN-S-3@1--archived.md", "AN-S-3", "archived", 1)
        archive_roots = [archived.parent.relative_to(self.root).as_posix()]
        disabled, enabled = StringIO(), StringIO()
        with patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "0"}), redirect_stderr(disabled):
            expected = native_carrier_hashes(binding, foreground=True)
        self.assertEqual("", disabled.getvalue())
        with (patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1"}), redirect_stderr(enabled),
              patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={})):
            self.assertEqual(expected, native_carrier_hashes(binding, foreground=True))
            native_carrier_hashes(binding, archive_roots=archive_roots)
            prepare_generation_snapshot(binding, archive_stage="foreground")
        prefix = "ANECHOIC_STARTUP_TIMING "
        lines = enabled.getvalue().splitlines()
        self.assertTrue(all(line.startswith(prefix) for line in lines), lines)
        records = [json.loads(line.removeprefix(prefix)) for line in lines]
        self.assertEqual([("scan_started", "foreground_hashes"), ("scan_metrics", "foreground_hashes"),
                          ("scan_started", "foreground_capture"), ("non_archived_load_started", "foreground_capture"),
                          ("scan_metrics", "foreground_capture")], [(row["phase"], row["mode"]) for row in records])
        for row in records:
            self.assertIs(type(row["timestamp_ns"]), int)
            self.assertGreater(row["timestamp_ns"], 0)
            if row["phase"] == "scan_metrics":
                self.assertEqual(2, row["carrier_count"])
                self.assertEqual(self.manifest.stat().st_size + current.stat().st_size, row["bytes_read"])
                for field in ("census_ns", "guarded_read_ns", "stream_ns", "sha256_ns"):
                    self.assertIs(type(row[field]), int)
                    self.assertGreaterEqual(row[field], 0)
                self.assertLessEqual(row["stream_ns"], row["guarded_read_ns"])
        self.assertNotIn(str(self.root), enabled.getvalue())

    def test_managed_snapshot_can_delegate_final_currentness_to_watcher(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config",
                   return_value={}), patch.object(ReadContext, "currentness") as currentness:
            _, finish = prepare_generation_snapshot(binding, watcher_guarded=True)
            self.assertTrue(finish(endpoints)["atoms"])
        currentness.assert_not_called()

    def test_snapshot_and_ticket_delta_optional_hashes(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        path = self.write("AN-T-8--hash.md", "AN-T-8", "active", 1)
        relative = path.relative_to(self.root).as_posix()
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={}):
            _, finish = prepare_generation_snapshot(binding, include_hashes=True)
            snap, hashes = finish(endpoints)
            self.assertEqual(native_carrier_hashes(binding), hashes)
            _, default_finish = prepare_generation_snapshot(binding)
            self.assertIsInstance(default_finish(endpoints), dict)
        self.assertTrue(snap["atoms"])
        delta = capture_ticket_delta(binding, [relative], endpoints, include_hashes=True)
        self.assertEqual({relative: sha256(path.read_bytes()).hexdigest()}, delta["carrier_hashes"])
        path.unlink()
        deleted = capture_ticket_delta(binding, [relative], endpoints, include_hashes=True)
        self.assertEqual({}, deleted["carrier_hashes"])
        self.assertEqual([[path.parent.relative_to(self.root).as_posix(), path.name]], deleted["paths"])

    def test_generation_defers_only_intermediate_currentness_check(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        path = self.write("AN-S-2--source.md", "AN-S-2", "active", 1)
        original = ReadContext.currentness
        calls = []

        def currentness(reader):
            calls.append(reader)
            return original(reader)

        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config",
                   return_value={}), patch.object(ReadContext, "currentness", currentness):
            _, finish = prepare_generation_snapshot(binding)
            self.assertEqual([], calls)
            path.write_text(path.read_text().replace("Example", "Changed"), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed during generation"):
                finish({"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                         "CONTAINS": [{}, True]})
            self.assertEqual(1, len(calls))

        calls.clear()
        with patch.object(ReadContext, "currentness", currentness):
            capture_native(self.selection)
        self.assertEqual(1, len(calls))

    def test_generation_indexes_first_summary_for_current_and_archived_atoms(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        original_summary = "\n# Summary\n\nLegacy wording\n"
        archive = self.write("AN-S-2@1--source.md", "AN-S-2", "archived", 1)
        archive.write_text(archive.read_text().replace("\n---\n\n## Summary", "\n---\n## Summary").replace("Example\n", "Example\n\nMore detail\n") + original_summary)
        current = self.write("AN-S-2--source.md", "AN-S-2", "active", 2)
        current.write_text(current.read_text().replace("Example\n", "Example\n\nMore detail\n") + original_summary)
        legacy = self.write("AN-S-3--legacy.md", "AN-S-3", "active", 1)
        legacy.write_text(legacy.read_text().replace("## Summary\n\nExample", "Summary\n=======\n\nLegacy title"))
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                     "CONTAINS": [{}, True]}
        with (patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config",
                    return_value={}), patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.source_row__pub.parse_content",
                                            side_effect=AssertionError("Generation must not build Content Properties"))):
            _, finish = prepare_generation_snapshot(binding)
            summaries = {atom["exact_ref"]: atom["summary"] for atom in finish(endpoints)["atoms"]}
        self.assertEqual("Example", summaries["AN-S-2@1"])
        self.assertEqual("Example", summaries["AN-S-2@2"])
        self.assertEqual("Legacy title", summaries["AN-S-3@1"])
        self.assertIn("More detail", current.read_text())
        self.assertIn("More detail", archive.read_text())

    def test_model_capture_retains_full_body_and_exact_ref(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        path = self.write("LAYER_1_META_ONTOLOGY_C9/_SPEC/AN-S-2--model.md", "AN-S-2", "active", 2)
        path.write_text(path.read_text().replace("Example\n", "Example\n\nFull detail\n"))
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={}):
            _, finish, inputs = prepare_generation_snapshot(binding, include_model_inputs=True)
            result = finish({"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]})
        row, = inputs["rows"]
        self.assertEqual("AN-S-2@2", row["exact_ref"])
        self.assertIn("Full detail", row["body"])
        self.assertEqual("Example", next(atom["summary"] for atom in result["atoms"] if atom["reference"] == "AN-S-2"))
        self.assertTrue(inputs["has_c9"])

    def test_generation_validates_with_a_separate_read_budget(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                     "CONTAINS": [{}, True]}
        clock = monotonic()
        module = prepare_generation_snapshot.__module__
        verify = ReadContext.currentness

        def timed_capture(*args, **kwargs):
            nonlocal clock
            captured = capture_native(*args, **kwargs)
            clock += 299
            return captured

        def timed_verification(reader):
            nonlocal clock
            clock += 2
            return verify(reader)

        with (patch(f"{module}._graph_config", return_value={}),
              patch(f"{module}.capture_native", timed_capture),
              patch.object(ReadContext, "currentness", timed_verification),
              patch(f"{module}.monotonic", lambda: clock),
              patch("time.monotonic", lambda: clock)):
            _, finish = prepare_generation_snapshot(binding)
            clock += 400
            self.assertTrue(finish(endpoints)["atoms"])
