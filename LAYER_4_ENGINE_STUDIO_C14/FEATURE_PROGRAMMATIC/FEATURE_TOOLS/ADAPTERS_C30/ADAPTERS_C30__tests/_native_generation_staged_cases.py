"""Native generation test cases."""

from pathlib import Path
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
    ADAPTERS_C30__shared import (
    ReadContext,
    prepare_generation_snapshot,
    status_domains,
)  # fmt: skip


class NativeGenerationStagedCases:
    def test_generation_capture_uses_admitted_status_domains(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        domains = status_domains({})
        domains["C"] = domains["P"] = domains["C"] | {"reviewed"}
        self.write(
            "__PROJECT_CONFIG/AN-C-1--valid.md", "AN-C-1", "reviewed", 1
        )
        unknown = self.write(
            "__PROJECT_CONFIG/AN-C-2--unknown.md", "AN-C-2", "unknown", 1
        )
        with patch(
            "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
            "native_snapshot_cli._graph_config",
            return_value={},
        ):
            _, finish = prepare_generation_snapshot(binding)
            result = finish(
                {
                    "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
                    "CONTAINS": [{}, True],
                },
                domains,
            )
        row = next(
            row for row in result["atoms"] if row["reference"] == "AN-C-1"
        )
        self.assertEqual(
            ("reviewed", "Current"), (row["status"], row["status_group"])
        )
        self.assertIn(
            unknown.relative_to(self.root).as_posix(),
            {issue["relative_path"] for issue in result["ingestion_issues"]},
        )

    def test_atom_projection_uses_authored_header_context(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            native_generation_snapshot import (_atoms)  # fmt: skip

        rows = self._projection_rows(_atoms)
        self.assertEqual(
            ("C42", 2, "DES"),
            tuple(
                rows[0][key]
                for key in ("container_component", "tier", "template")
            ),
        )
        self.assertEqual(
            (None, None, None),
            tuple(
                rows[1][key]
                for key in ("container_component", "tier", "template")
            ),
        )

    def _projection_rows(self, _atoms):
        base = {
            "ref": "AN-S-2",
            "_exact_ref": "AN-S-2@1",
            "status_group": "Current",
            "source_path": "spec.md",
            "_summary_title": "Example",
            "status": "active",
            "version": 1,
        }
        context = {
            "container": {"component": "C42"},
            "tier": 2,
            "template": "DES",
        }
        rows = _atoms(
            [
                base
                | {
                    "header_json": {
                        "atom_family": "SPEC",
                        "atom_id": "AN-S-2",
                        "container": context["container"],
                        "tier": 2,
                        "context": {"template": "DES"},
                        "state": {
                            "status": "active",
                            "version": 1,
                            "updated_at": "2026-11-19T00:00:00Z",
                        },
                    }
                },
                base
                | {
                    "ref": "AN-S-3",
                    "header_json": {
                        "context": {"container": {"atom": "AN-S-2"}}
                    },
                },
            ]
        )
        return rows

    def \
   test_staged_capture_reads_archives_without_reopening_foreground_carriers(
        self,
    ):  # fmt: skip
        (
            binding,
            current,
            draft,
            off_path,
            archived,
            installed,
            endpoints,
        ) = self._staged_fixture()
        reads, stats = [], []
        read, lstat = ReadContext.read, Path.lstat

        def record_read(reader, path, **options):
            reads.append(path)
            return read(reader, path, **options)

        def record_lstat(path):
            stats.append(path)
            return lstat(path)

        with (
            patch.object(ReadContext, "read", record_read),
            patch.object(Path, "lstat", record_lstat),
            patch(
                "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                "native_snapshot_cli._graph_config",
                return_value={},
            ),
        ):
            roots = self._check_foreground_capture(
                binding,
                endpoints,
                current,
                draft,
                off_path,
                archived,
                installed,
                reads,
                stats,
            )

            self._check_archive_capture(
                binding, endpoints, roots, archived, reads
            )

    def _check_archive_capture(
        self, binding, endpoints, roots, archived, reads
    ):
        reads.clear()
        graph, finish = prepare_generation_snapshot(
            binding,
            include_hashes=True,
            archive_stage="archive",
            archive_roots=roots,
        )
        archive_snapshot, archive_hashes = finish(endpoints)
        self.assertIsNone(graph)
        self.assertEqual({archived, self.manifest}, set(reads))
        self.assertEqual(
            {archived}, {self.root / path for path in archive_hashes}
        )
        self.assertEqual(
            ["AN-S-4@1"],
            [row["reference"] for row in archive_snapshot["atoms"]],
        )
        self.assertIn(
            {
                "source_kind": "Atom",
                "source_ref": "AN-S-2",
                "target_kind": "Atom",
                "target_ref": "AN-S-4@1",
                "relation_type": "CONTAINS",
                "derived": True,
            },
            archive_snapshot["relations"],
        )

    def _check_foreground_capture(
        self,
        binding,
        endpoints,
        current,
        draft,
        off_path,
        archived,
        installed,
        reads,
        stats,
    ):
        _, finish = prepare_generation_snapshot(
            binding, archive_stage="foreground"
        )
        foreground, hashes, roots, off_path_snapshot, off_path_hashes = finish(
            endpoints
        )
        self.assertEqual(
            {"AN-S-001", "AN-S-2", "AN-S-2@3-draft"},
            {row["reference"] for row in foreground["atoms"]},
        )
        self.assertEqual(
            {self.manifest, current, draft},
            {self.root / path for path in hashes},
        )
        self.assertEqual(
            ["AN-S-3@1"],
            [row["reference"] for row in off_path_snapshot["atoms"]],
        )
        self.assertEqual(
            {off_path}, {self.root / path for path in off_path_hashes}
        )
        self._assert_foreground_reads(
            archived, installed, off_path, roots, reads, stats
        )

        return roots

    def _staged_fixture(self):
        binding = {
            "root": str(self.root),
            "control_root": self.control.name,
            "manifest_path": self.manifest.relative_to(self.root).as_posix(),
            "manifest_sha256": self.selection.manifest_sha256,
            "project_prefix": "AN",
        }
        current = self.write("AN-S-2--current.md", "AN-S-2", "active", 2)
        draft = self.write(
            "01_draft/AN-S-2@3-draft--draft.md", "AN-S-2", "draft", 3
        )
        off_path = self.write("AN-S-3@1--off-path.md", "AN-S-3", "archived", 1)
        archived = self.write(
            "09_archived/AN-S-4@1--archived.md",
            "AN-S-4",
            "archived",
            1,
            {"atom": "AN-S-2"},
        )
        installed = self.write(
            "000_ANECHOIC_framework/09_archived/AN-S-5@1--installed.md",
            "AN-S-5",
            "archived",
            1,
        )
        endpoints = {
            "CONTAINED_BY": [{"inverse_alias": "CONTAINS"}, False],
            "CONTAINS": [{}, True],
        }
        return (
            binding,
            current,
            draft,
            off_path,
            archived,
            installed,
            endpoints,
        )
