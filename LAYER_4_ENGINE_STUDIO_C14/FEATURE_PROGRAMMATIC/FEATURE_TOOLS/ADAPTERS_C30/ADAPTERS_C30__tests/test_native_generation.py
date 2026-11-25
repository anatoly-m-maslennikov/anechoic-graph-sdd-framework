from hashlib import sha256
from pathlib import Path
from time import monotonic
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext, capture_native, capture_ticket_delta, native_carrier_hashes, prepare_generation_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_generation_snapshot import _authored_edges


class NativeGenerationTests(NativeCaptureFixture, unittest.TestCase):
    def test_retired_citation_relations_are_omitted_from_archive_edges(self):
        row = {"ref": "AN-S-1@1", "status_group": "Archived", "header_json": {"relations": {
            "IS_REFERENCE": ["AN-S-2"], "REFERENCES": ["AN-S-3"], "SERVES": ["AN-S-4"],
        }}}
        archived = list(_authored_edges(row, {"SERVES"}, {}))
        self.assertEqual(["SERVES"], [edge["relation_type"] for edge in archived])

        registered = list(_authored_edges(row, {"SERVES", "IS_REFERENCE", "HAS_REFERENCE"},
                                          {"IS_REFERENCE": "HAS_REFERENCE"}))
        self.assertEqual(["IS_REFERENCE", "IS_REFERENCE", "SERVES"],
                         [edge["relation_type"] for edge in registered])

        current = list(_authored_edges(dict(row, status_group="Current"), {"SERVES"}, {}))
        self.assertEqual(["IS_REFERENCE", "REFERENCES", "SERVES"],
                         [edge["relation_type"] for edge in current])

    def test_historical_relation_names_normalize_to_declared_names(self):
        pairs = {"CONTAINED_BY": "IS_CONTAINED_BY", "CHILD_OF": "IS_CHILD_OF",
                 "CHILDREN": "IS_PARENT_FOR", "NARROWER_THAN": "IS_NARROWER_THAN",
                 "INSTANCE_OF": "IS_INSTANCE_OF"}
        row = {"ref": "AN-S-1", "header_json": {"relations": {key: ["AN-S-2"] for key in pairs}}}
        edges = list(_authored_edges(row, set(pairs.values()), {}))
        self.assertEqual(set(pairs.values()), {edge["relation_type"] for edge in edges})

    def test_model_inputs_share_capture_and_report_quarantined_candidates(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        ontology = "ONTOLOGY_SCORE_C82/CONTINUANT_PITCHFORK_C9"
        path = self.write(f"{ontology}/_SPEC/AN-S-2--model.md", "AN-S-2", "active", 2)
        body = "\n## Summary\n\nExample\n\nFull Summary detail.\n"
        path.write_bytes(path.read_bytes().replace(b"\n## Summary\n\nExample\n", body.encode("utf-8")))
        self.write(f"{ontology}/deep/nested/AN-S-3--other.md", "AN-S-3", "active", 1)
        self.write("002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-4@1-draft--draft.md", "AN-C-4", "draft", 1)
        bad = self.control / "002_PROJECT_CONFIG/CUSTOM_MODEL/AN-C-5--bad.md"
        bad.write_text("---\ninvalid: [\n---\n", encoding="utf-8")
        reads = []
        original = ReadContext.read

        def record(reader, source, **options):
            reads.append(source)
            return original(reader, source, **options)

        with patch.object(ReadContext, "read", record), patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={}
        ):
            _, finish, inputs = prepare_generation_snapshot(binding, include_model_inputs=True)
            self.assertTrue(inputs["has_c9"])
            self.assertEqual(1, len(inputs["rows"]))
            row = inputs["rows"][0]
            self.assertEqual(f"{ontology}/_SPEC/AN-S-2--model.md", row["source_path"])
            self.assertEqual("AN-S-2@2", row["exact_ref"])
            self.assertEqual("AN-S-2", row["metadata"]["identity"]["atom_id"])
            self.assertEqual(body, row["body"])
            self.assertEqual(bad.relative_to(self.root).as_posix(), inputs["issues"][0]["relative_path"])
            self.assertEqual(1, reads.count(path))
            with self.assertRaises(TypeError):
                inputs["has_c9"] = False
            snapshot = finish({"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]})
            atom = next(atom for atom in snapshot["atoms"] if atom["reference"] == "AN-S-2")
            self.assertEqual("Example", atom["summary"])
            with self.assertRaises(ValueError):
                prepare_generation_snapshot(binding)

    def test_model_inputs_empty_c9_and_non_model_errors(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        (self.control / "LAYER_1_META_ONTOLOGY_C9").mkdir()
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config", return_value={}):
            _, _, inputs = prepare_generation_snapshot(binding, include_model_inputs=True)
            self.assertTrue(inputs["has_c9"])
            self.assertEqual((), inputs["rows"])
            (self.control / "AN-S-9--bad.md").write_text("---\ninvalid: [\n---\n")
            with self.assertRaises(ValueError):
                prepare_generation_snapshot(binding, include_model_inputs=True)

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
        endpoints = {"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
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
        with self.assertRaisesRegex(ValueError, "non-Archived Atom") as error:
            prepare_generation_snapshot(binding, archive_stage="archive",
                                        archive_roots=[path.parent.relative_to(self.root).as_posix()])
        self.assertEqual(relative, error.exception.ingestion_issues[0]["relative_path"])

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

    def test_managed_snapshot_can_delegate_final_currentness_to_watcher(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        endpoints = {"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
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
        endpoints = {"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
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
                finish({"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
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
        archive.write_text(archive.read_text().replace("\n---\n\n## Summary", "\n---\n## Summary") + original_summary)
        current = self.write("AN-S-2--source.md", "AN-S-2", "active", 2)
        current.write_text(current.read_text() + original_summary)
        endpoints = {"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                     "CONTAINS": [{}, True]}
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config",
                   return_value={}):
            _, finish = prepare_generation_snapshot(binding)
            summaries = {atom["exact_ref"]: atom["summary"] for atom in finish(endpoints)["atoms"]}
        self.assertEqual("Example", summaries["AN-S-2@1"])
        self.assertEqual("Example", summaries["AN-S-2@2"])

    def test_generation_validates_with_a_separate_read_budget(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        endpoints = {"IS_CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
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
