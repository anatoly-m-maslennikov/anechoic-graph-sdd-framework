from hashlib import sha256
from time import monotonic
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext, capture_native, capture_ticket_delta, native_carrier_hashes, prepare_generation_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)


class NativeGenerationTests(NativeCaptureFixture, unittest.TestCase):
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
        archive.write_text(archive.read_text().replace("\n---\n\n## Summary", "\n---\n## Summary") + original_summary)
        current = self.write("AN-S-2--source.md", "AN-S-2", "active", 2)
        current.write_text(current.read_text() + original_summary)
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
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
