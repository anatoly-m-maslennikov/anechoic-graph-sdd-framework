"""Applicable Methodology compilation behavior."""

import importlib
from pathlib import Path
from unittest import mock

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__shared import (
    SETTINGS_PATH,
)

BASE = (
    "FEATURE_PROGRAMMATIC.FEATURE_TOOLS."
    "COMPILE_APPLICABLE_METHODOLOGY."
    "COMPILE_APPLICABLE_METHODOLOGY__tests."
)
support = importlib.import_module(BASE + "methodology_test_support")
phases = importlib.import_module(BASE + "methodology_conflict_phases")
CompilerFixture = support.CompilerFixture
module = support.module
carrier = support.carrier

mixin = importlib.import_module(BASE + "methodology_conflict_mixin")


class CompilerTest(mixin.ConflictMixin, CompilerFixture):
    def test_changed_control_root_blocks_staging_at_original_places(
        self,
    ) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "05_method",
            "CA-M-001--one.md",
            carrier("CA-M-001"),
        )
        places = module.methodology_paths(self.temp)
        _, candidates, snapshot = module.compile_report(self.temp, places)
        (self.temp / SETTINGS_PATH).write_text(
            '[project]\nname = "anechoic"\n[paths]\n'
            'control_root = ".anechoic_other_project"\n'
        )

        with self.assertRaises(module.CompileError) as raised:
            module.stage_outputs(self.temp, candidates, snapshot, places)

        self.assertEqual("source-frontier-changed", raised.exception.code)
        self.assertFalse((self.temp / places.output / "05_method").exists())
        self.assertFalse((self.temp / ".anechoic_other_project").exists())

    # fmt: off
    def \
    test_explicit_release_child_places_remain_independent_of_canonical_target(
        self,
    ) -> None:
        # fmt: on
        original = self.write(
            "001_CORE_META_MODEL",
            "05_method",
            "CA-M-001--one.md",
            carrier("CA-M-001"),
        )
        canonical = module.methodology_paths(self.temp)
        child_output = (
            canonical.output / "_release_materialized/selected-candidate"
        )
        places = module.MethodologyPaths(
            source=canonical.source,
            output=child_output,
            declaration_digest=canonical.declaration_digest,
            control_root=canonical.control_root,
        )

        report, selected, snapshot = module.compile_report(self.temp, places)
        staging = module.stage_outputs(self.temp, selected, snapshot, places)
        module.replace_outputs_atomically(self.temp, staging, places)

        projected = self.temp / child_output / "05_method" / original.name
        self.assertTrue(report["can_apply"])
        self.assertEqual(
            projected.relative_to(self.temp).as_posix(),
            report["output_plan"][0]["output_path"],
        )
        self.assertIn(b"projection:", projected.read_bytes())
        self.assertEqual(carrier("CA-M-001"), original.read_bytes())
        self.assertFalse((self.temp / canonical.output / "05_method").exists())


    def test_duplicate_identity_blocks_apply_without_exact_approval(
        self,
    ) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-001-A--one.md",
            carrier("CA-R-001"),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "04_requirement",
            "CA-R-001-B--two.md",
            carrier("CA-R-001", version=2),
        )
        code, report = self.invoke()
        self.assertEqual(code, 2)
        self.assertGreaterEqual(report["conflict_count"], 1)
        self.assertIn(
            "duplicate_selected_atom_identity",
            {item["type"] for item in report["conflicts"]},
        )
        apply_code, applied = self.invoke("--apply")
        self.assertEqual(apply_code, 2)
        self.assertFalse(applied["can_apply"])
        for _, role in module.ROLES:
            self.assertFalse((self.temp / self.output / role).exists())


    def test_output_collision_is_reported(self) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "SHARED--claim.md",
            carrier("CA-R-001"),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "04_requirement",
            "SHARED--claim.md",
            carrier("CA-R-002"),
        )
        code, report = self.invoke()
        self.assertEqual(code, 2)
        self.assertIn(
            "output_path_collision",
            {item["type"] for item in report["conflicts"]},
        )


    def test_dry_run_reports_all_five_conflict_classes(self) -> None:
        phases.write_first_conflicts(self)
        phases.write_remaining_conflicts(self)
        code, report = self.invoke()
        self.assertEqual(code, 2)
        self.assertEqual(
            {item["type"] for item in report["conflicts"]},
            {
                "duplicate_selected_atom_identity",
                "unresolved_replacement",
                "incompatible_retained_candidates",
                "unresolved_priority",
                "output_path_collision",
            },
        )


    def test_drafts_archives_cap_and_implementation_are_excluded(self) -> None:
        active = self.write(
            "001_CORE_META_MODEL",
            "09_operations",
            "CA-O-001-OPERATIONS--active.md",
            carrier("CA-O-001"),
        )
        original = active.read_bytes()
        for index, directory in enumerate(
            ("draft", "drafts", "archive", "archived", "Draft", "Archived")
        ):
            historical = (
                active.parent / f"copy-{index}" / directory / active.name
            )
            historical.parent.mkdir(parents=True)
            historical.write_bytes(original)
        (self.layers["CORE_META_MODEL"] / "01_concern").mkdir()
        (
            self.layers["CORE_META_MODEL"] / "01_concern/CA-C-001.md"
        ).write_bytes(carrier("CA-C-001"))
        (self.layers["CORE_META_MODEL"] / "08_implementation").mkdir()
        (
            self.layers["CORE_META_MODEL"] / "08_implementation/CA-I-001.md"
        ).write_bytes(carrier("CA-I-001"))
        code, report = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(report["eligible_candidate_count"], 1)
        self.assertEqual(report["conflict_count"], 0)
        self.assertEqual(
            report["output_plan"][0]["source_carrier_path"],
            active.relative_to(self.temp).as_posix(),
        )
        self.assertEqual(original, active.read_bytes())


    def test_failed_multi_directory_swap_rolls_back(self) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-001--one.md",
            carrier("CA-R-001"),
        )
        self.write(
            "001_CORE_META_MODEL",
            "05_method",
            "CA-M-001--two.md",
            carrier("CA-M-001"),
        )
        code, _ = self.invoke("--apply")
        self.assertEqual(code, 0)
        output = self.temp / self.output
        before = {
            path.relative_to(output): path.read_bytes()
            for path in output.rglob("*.md")
        }
        _, selected, snapshot = module.compile_report(self.temp)
        staging = module.stage_outputs(self.temp, selected, snapshot)
        real_replace = module.os.replace
        calls = 0

        def fail_once(source: Path, target: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected")
            real_replace(source, target)

        with mock.patch.object(module.os, "replace", side_effect=fail_once):
            with self.assertRaises(module.CompileError):
                module.replace_outputs_atomically(self.temp, staging)
        after = {
            path.relative_to(output): path.read_bytes()
            for path in output.rglob("*.md")
        }
        self.assertEqual(before, after)
