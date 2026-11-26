from hashlib import sha256
import os
import unittest
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext, capture_ticket_delta, native_carrier_hashes, prepare_generation_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__tests.ADAPTERS_C30__tests__shared import (
    NativeCaptureFixture,
)


class NativeGenerationBoundaryTests(NativeCaptureFixture, unittest.TestCase):
    def test_archive_capture_and_hash_readers_have_no_timeout(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        archived = self.write("09_archived/AN-S-4@1--archived.md", "AN-S-4", "archived", 1)
        roots = [archived.parent.relative_to(self.root).as_posix()]
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
        observed = []
        initialize_reader = ReadContext.__init__

        def reader(context, **kwargs):
            initialize_reader(context, **kwargs)
            observed.append(context.limits.copy())
            if "timeout_seconds" not in context.limits:
                context.started -= 10000

        prefix = "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
        with (patch.object(ReadContext, "__init__", reader),
              patch.dict(os.environ, {"ANECHOIC_STARTUP_TIMING": "1", "ANECHOIC_TEST_IMAGE_DEADLINES": "1"}),
              patch(prefix + "native_snapshot_cli._graph_config", return_value={})):
            for stage in ("archive", "foreground", None):
                _, finish = prepare_generation_snapshot(binding, archive_stage=stage,
                                                        archive_roots=roots if stage == "archive" else ())
                finish(endpoints)
            native_carrier_hashes(binding, archive_roots=roots)
            native_carrier_hashes(binding, foreground=True)
            native_carrier_hashes(binding)
        self.assertEqual([None, 300, 300, None, 300, 300], [limits.get("timeout_seconds") for limits in observed])
        caps = {key: value for key, value in observed[1].items() if key != "timeout_seconds"}
        for limits in observed:
            self.assertEqual(caps, {key: value for key, value in limits.items() if key != "timeout_seconds"})

    def test_delta_skips_unknown_relation_and_keeps_both_tickets(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        invalid = self.write("AN-T-8--invalid.md", "AN-T-8", "active", 1)
        invalid.write_text(invalid.read_text().replace("state:", "relations: {UNDECLARED: [AN-T-9]}\nstate:"))
        valid = self.write("AN-T-9--valid.md", "AN-T-9", "active", 1)
        paths = [path.relative_to(self.root).as_posix() for path in (invalid, valid)]
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
        result = capture_ticket_delta(binding, paths, endpoints, include_hashes=True)
        snapshot = result["snapshot"]
        self.assertEqual(["AN-T-8", "AN-T-9"], [row["reference"] for row in snapshot["atoms"]])
        self.assertEqual(set(paths), result["carrier_hashes"].keys())
        issue, = snapshot["ingestion_issues"]
        self.assertEqual((paths[0], "AN-T-8@1", "undeclared_relation"),
                         (issue["relative_path"], issue["atom_ref"], issue["code"]))
        self.assertIn("Undeclared native relation", issue["message"])

    def test_unknown_relation_still_validates_targets_and_schema(self):
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": self.selection.manifest_sha256, "project_prefix": "AN"}
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True]}
        for targets, message in (("[invalid]", "Invalid native relation target"),
                                 ("invalid", "Native relation targets must be a list")):
            with self.subTest(targets=targets):
                path = self.write("AN-T-8--invalid.md", "AN-T-8", "active", 1)
                path.write_text(path.read_text().replace("state:", f"relations: {{UNDECLARED: {targets}}}\nstate:"))
                snapshot = capture_ticket_delta(binding, [path.relative_to(self.root).as_posix()], endpoints)["snapshot"]
                self.assertEqual([], snapshot["atoms"])
                issue, = snapshot["ingestion_issues"]
                self.assertEqual(("invalid_value", message), (issue["code"], issue["message"]))

    def test_manifest_and_worktree_keep_valid_edges_when_relation_is_unknown(self):
        current = self.write("AN-S-2--current.md", "AN-S-2", "active", 1)
        for path in (self.manifest, current):
            path.write_text(path.read_text().replace(
                "state:", "relations: {SERVES: [AN-S-2], LINKS: [AN-S-2]}\nstate:"))
        binding = {"root": str(self.root), "control_root": self.control.name,
                   "manifest_path": self.manifest.relative_to(self.root).as_posix(),
                   "manifest_sha256": sha256(self.manifest.read_bytes()).hexdigest(), "project_prefix": "AN"}
        endpoints = {"CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False], "CONTAINS": [{}, True],
                     "LINKS": [{}, False]}
        with patch("FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.native_snapshot_cli._graph_config",
                   return_value={}):
            for stage in (None, "foreground"):
                with self.subTest(stage=stage):
                    _, finish = prepare_generation_snapshot(binding, archive_stage=stage)
                    result = finish(endpoints)
                    snapshot = result[0] if stage else result
                    self.assertEqual({"AN-S-001", "AN-S-2"}, {row["reference"] for row in snapshot["atoms"]})
                    links = [edge for edge in snapshot["relations"] if edge["relation_type"] == "LINKS"]
                    self.assertEqual({"AN-S-001", "AN-S-2"}, {edge["source_ref"] for edge in links})
                    self.assertFalse(any(edge["relation_type"] == "SERVES" for edge in snapshot["relations"]))
                    self.assertEqual({(path.relative_to(self.root).as_posix(), ref, "Undeclared native relation: SERVES")
                                      for path, ref in ((self.manifest, "AN-S-001@1"), (current, "AN-S-2@1"))},
                                     {(issue["relative_path"], issue["atom_ref"], issue["message"])
                                      for issue in snapshot["ingestion_issues"]})
