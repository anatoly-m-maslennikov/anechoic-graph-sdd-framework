"""Native generation test cases."""

from hashlib import sha256
from time import monotonic
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    ReadContext,
    capture_ticket_delta,
    native_carrier_hashes,
    prepare_generation_snapshot,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.native_source_rows__pub import (
    capture_native,
)


class NativeGenerationMiscCases:
    def test_snapshot_and_ticket_delta_optional_hashes(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        path = self.write("AN-T-8--hash.md", "AN-T-8", "active", 1)
        relative = path.relative_to(self.root).as_posix()
        endpoints = {
            "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
            "CONTAINS": [{}, True],
        }
        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
            "native_snapshot_cli._graph_config",
            return_value={},
        ):
            _, finish = prepare_generation_snapshot(
                binding, include_hashes=True
            )
            snap, hashes = finish(endpoints)
            self.assertEqual(native_carrier_hashes(binding), hashes)
            _, default_finish = prepare_generation_snapshot(binding)
            self.assertIsInstance(default_finish(endpoints), dict)
        self.assertTrue(snap["atoms"])
        delta = capture_ticket_delta(
            binding, [relative], endpoints, include_hashes=True
        )
        self.assertEqual(
            {relative: sha256(path.read_bytes()).hexdigest()},
            delta["carrier_hashes"],
        )
        path.unlink()
        deleted = capture_ticket_delta(
            binding, [relative], endpoints, include_hashes=True
        )
        self.assertEqual({}, deleted["carrier_hashes"])
        self.assertEqual(
            [[path.parent.relative_to(self.root).as_posix(), path.name]],
            deleted["paths"],
        )

    def test_generation_defers_only_intermediate_currentness_check(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        path = self.write("AN-S-2--source.md", "AN-S-2", "active", 1)
        original = ReadContext.currentness
        calls = []

        def currentness(reader):
            calls.append(reader)
            return original(reader)

        with (
            patch(
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "native_snapshot_cli._graph_config",
                return_value={},
            ),
            patch.object(ReadContext, "currentness", currentness),
        ):
            _, finish = prepare_generation_snapshot(binding)
            self.assertEqual([], calls)
            path.write_text(
                path.read_text().replace("Example", "Changed"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError, "changed during generation"
            ):
                finish(
                    {
                        "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                        "CONTAINS": [{}, True],
                    }
                )
            self.assertEqual(1, len(calls))

        calls.clear()
        with patch.object(ReadContext, "currentness", currentness):
            capture_native(self.selection)
        self.assertEqual(1, len(calls))

    def test_generation_indexes_first_summary_for_current_and_archived_atoms(
        self,
    ):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        current, archive = self._summary_fixtures()
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
            patch(
                'FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.source_row__pub.parse_content',
                side_effect=AssertionError(
                    "Generation must not build Content Properties"
                ),
            ),
        ):
            _, finish = prepare_generation_snapshot(binding)
            summaries = {
                atom["exact_ref"]: atom["summary"]
                for atom in finish(endpoints)["atoms"]
            }
        self.assertEqual("Example", summaries["AN-S-2@1"])
        self.assertEqual("Example", summaries["AN-S-2@2"])
        self.assertEqual("Legacy title", summaries["AN-S-3@1"])
        self.assertIn("More detail", current.read_text())
        self.assertIn("More detail", archive.read_text())

    def _summary_fixtures(self):
        original_summary = "\n# Summary\n\nLegacy wording\n"
        archive = self.write("AN-S-2@1--source.md", "AN-S-2", "archived", 1)
        archive.write_text(
            archive.read_text()
            .replace("\n---\n\n## Summary", "\n---\n## Summary")
            .replace("Example\n", "Example\n\nMore detail\n")
            + original_summary
        )
        current = self.write("AN-S-2--source.md", "AN-S-2", "active", 2)
        current.write_text(
            current.read_text().replace(
                "Example\n", "Example\n\nMore detail\n"
            )
            + original_summary
        )
        legacy = self.write("AN-S-3--legacy.md", "AN-S-3", "active", 1)
        legacy.write_text(
            legacy.read_text().replace(
                "## Summary\n\nExample", "Summary\n=======\n\nLegacy title"
            )
        )
        return current, archive

    def test_model_capture_retains_full_body_and_exact_ref(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        path = self.write(
            "LAYER_1_META_ONTOLOGY_C9/_SPEC/AN-S-2--model.md",
            "AN-S-2",
            "active",
            2,
        )
        path.write_text(
            path.read_text().replace("Example\n", "Example\n\nFull detail\n")
        )
        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
            "native_snapshot_cli._graph_config",
            return_value={},
        ):
            _, finish, inputs = prepare_generation_snapshot(
                binding, include_model_inputs=True
            )
            result = finish(
                {
                    "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                    "CONTAINS": [{}, True],
                }
            )
        (row,) = inputs["rows"]
        self.assertEqual("AN-S-2@2", row["exact_ref"])
        self.assertIn("Full detail", row["body"])
        self.assertEqual(
            "Example",
            next(
                atom["summary"]
                for atom in result["atoms"]
                if atom["reference"] == "AN-S-2"
            ),
        )
        self.assertTrue(inputs["has_c9"])

    def test_generation_validates_with_a_separate_read_budget(self):
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

        with (
            patch(f"{module}._graph_config", return_value={}),
            patch(f"{module}.capture_native", timed_capture),
            patch.object(ReadContext, "currentness", timed_verification),
            patch(f"{module}.monotonic", lambda: clock),
            patch("time.monotonic", lambda: clock),
        ):
            _, finish = prepare_generation_snapshot(binding)
            clock += 400
            self.assertTrue(finish(endpoints)["atoms"])
