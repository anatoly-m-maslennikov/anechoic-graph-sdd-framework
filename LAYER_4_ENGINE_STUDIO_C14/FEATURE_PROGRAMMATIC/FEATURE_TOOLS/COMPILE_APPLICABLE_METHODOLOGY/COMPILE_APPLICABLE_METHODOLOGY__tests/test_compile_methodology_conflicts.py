"""Applicable Methodology compilation behavior."""

from pathlib import Path
from unittest import mock

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.COMPILE_APPLICABLE_METHODOLOGY__tests.methodology_test_support import (
    CompilerFixture, module, carrier, definition_carrier, term_definition_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.artifact_metadata import SETTINGS_PATH


class CompilerTest(CompilerFixture):
    def test_changed_control_root_blocks_staging_at_original_places(self) -> None:
        self.write("001_CORE_META_MODEL", "05_method", "CA-M-001--one.md", carrier("CA-M-001"))
        places = module.methodology_paths(self.temp)
        _, candidates, snapshot = module.compile_report(self.temp, places)
        (self.temp / SETTINGS_PATH).write_text(
            '[project]\nname = "anechoic"\n[paths]\ncontrol_root = ".anechoic_other_project"\n'
        )

        with self.assertRaises(module.CompileError) as raised:
            module.stage_outputs(self.temp, candidates, snapshot, places)

        self.assertEqual("source-frontier-changed", raised.exception.code)
        self.assertFalse((self.temp / places.output / "05_method").exists())
        self.assertFalse((self.temp / ".anechoic_other_project").exists())


    def test_explicit_release_child_places_remain_independent_of_canonical_target(self) -> None:
        original = self.write("001_CORE_META_MODEL", "05_method", "CA-M-001--one.md", carrier("CA-M-001"))
        canonical = module.methodology_paths(self.temp)
        child_output = canonical.output / "_release_materialized/selected-candidate"
        places = module.MethodologyPaths(
            source=canonical.source, output=child_output,
            declaration_digest=canonical.declaration_digest, control_root=canonical.control_root,
        )

        report, selected, snapshot = module.compile_report(self.temp, places)
        staging = module.stage_outputs(self.temp, selected, snapshot, places)
        module.replace_outputs_atomically(self.temp, staging, places)

        projected = self.temp / child_output / "05_method" / original.name
        self.assertTrue(report["can_apply"])
        self.assertEqual(projected.relative_to(self.temp).as_posix(), report["output_plan"][0]["output_path"])
        self.assertIn(b"projection:", projected.read_bytes())
        self.assertEqual(carrier("CA-M-001"), original.read_bytes())
        self.assertFalse((self.temp / canonical.output / "05_method").exists())


    def test_duplicate_identity_blocks_apply_without_exact_approval(self) -> None:
        self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001-A--one.md", carrier("CA-R-001"))
        self.write("003_PROJECT_CONFIGURATION", "04_requirement", "CA-R-001-B--two.md", carrier("CA-R-001", version=2))
        code, report = self.invoke()
        self.assertEqual(code, 2)
        self.assertGreaterEqual(report["conflict_count"], 1)
        self.assertIn("duplicate_selected_atom_identity", {item["type"] for item in report["conflicts"]})
        apply_code, applied = self.invoke("--apply")
        self.assertEqual(apply_code, 2)
        self.assertFalse(applied["can_apply"])
        for _, role in module.ROLES:
            self.assertFalse((self.temp / self.output / role).exists())


    def test_duplicate_governed_term_definition_blocks_apply(self) -> None:
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-010--define-shared-term.md",
            definition_carrier("CA-R-010", "Shared Term"),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "04_requirement",
            "CA-R-011--redefine-shared-term.md",
            definition_carrier("CA-R-011", "Shared Term", "Artifact/Type: Shared Term"),
        )

        code, report = self.invoke()

        self.assertEqual(2, code)
        conflict = next(
            row for row in report["conflicts"] if row["type"] == "duplicate_governed_term_definition"
        )
        self.assertEqual("Shared Term", conflict["details"]["term"])
        apply_code, applied = self.invoke("--apply")
        self.assertEqual(2, apply_code)
        self.assertFalse(applied["can_apply"])


    def test_current_and_legacy_term_definitions_conflict(self) -> None:
        current_subject = "ANECHOIC_MODEL <+ Term//Shared Term"
        self.write("001_CORE_META_MODEL", "05_method", "CA-M-010--define.md",
                   term_definition_carrier("CA-M-010", current_subject))
        self.write("003_PROJECT_CONFIGURATION", "05_method", "CA-M-011--define.md",
                   term_definition_carrier("CA-M-011", "Term//Shared Term"))
        self.write("003_PROJECT_CONFIGURATION", "04_requirement", "CA-R-012--define.md",
                   definition_carrier("CA-R-012", "Shared Term"))
        legacy_subject = "ANECHOIC_MODEL <+ Entity/Object/Continuant/Term//Shared Term"
        self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-013--define.md", (
            "---\natom_id: CA-R-013\nrole: Requirement\nform: Term Definition\n"
            f"subjects:\n  active: {legacy_subject}\n"
            "status: Active\nversion: 1\nrelations: {}\n---\n# Define Shared Term\n"
        ).encode())

        code, report = self.invoke()

        self.assertEqual(2, code)
        conflict = next(row for row in report["conflicts"] if row["type"] == "duplicate_governed_term_definition")
        self.assertEqual("Shared Term", conflict["details"]["term"])
        self.assertCountEqual(
            [current_subject, "Term//Shared Term", "Shared Term", legacy_subject],
            conflict["details"]["definition_subject_paths"].values(),
        )
        apply_code, applied = self.invoke("--apply")
        self.assertEqual(2, apply_code)
        self.assertFalse(applied["can_apply"])


    def test_separate_model_term_definitions_do_not_conflict(self) -> None:
        self.write("001_CORE_META_MODEL", "05_method", "CA-M-010--define.md",
                   term_definition_carrier("CA-M-010", "ANECHOIC_MODEL <+ Term//ID"))
        self.write("003_PROJECT_CONFIGURATION", "05_method", "CA-M-011--define.md",
                   term_definition_carrier("CA-M-011", "MODEL//Other <+ Term//ID"))

        code, report = self.invoke()

        self.assertEqual(0, code)
        self.assertNotIn("duplicate_governed_term_definition", {row["type"] for row in report["conflicts"]})


    def test_escaped_term_name_does_not_collide_with_model_qualified_term(self) -> None:
        self.write("001_CORE_META_MODEL", "05_method", "CA-M-010--define.md",
                   term_definition_carrier("CA-M-010", r"Term//MODEL\/\/Other \<\+ Term\/\/ID"))
        self.write("003_PROJECT_CONFIGURATION", "05_method", "CA-M-011--define.md",
                   term_definition_carrier("CA-M-011", "MODEL//Other <+ Term//ID"))

        code, report = self.invoke()

        self.assertEqual(0, code)
        self.assertNotIn("duplicate_governed_term_definition", {row["type"] for row in report["conflicts"]})

        output = {row["source_atom_id"]: row for row in report["output_plan"]}
        self.assertEqual(output["CA-M-010"]["definition_term"], output["CA-M-011"]["definition_term"])
        self.assertEqual(("", "MODEL//Other <+ Term//ID"),
                         (output["CA-M-010"]["definition_namespace"], output["CA-M-010"]["definition_term_name"]))
        self.assertEqual(("MODEL//Other", "ID"),
                         (output["CA-M-011"]["definition_namespace"], output["CA-M-011"]["definition_term_name"]))

        self.write("001_CORE_META_MODEL", "05_method", "CA-M-012--define.md",
                   term_definition_carrier("CA-M-012", "MODEL//Other <+ Term//ID"))
        self.write("003_PROJECT_CONFIGURATION", "05_method", "CA-M-013--define.md",
                   term_definition_carrier("CA-M-013", r"Term//MODEL\/\/Other \<\+ Term\/\/ID"))
        code, report = self.invoke()
        self.assertEqual(2, code)
        conflicts = [row["details"] for row in report["conflicts"] if row["type"] == "duplicate_governed_term_definition"]
        self.assertEqual(2, len(conflicts))
        self.assertEqual({"MODEL//Other <+ Term//ID"}, {row["term"] for row in conflicts})
        self.assertEqual({("", "MODEL//Other <+ Term//ID"), ("MODEL//Other", "ID")},
                         {(row["definition_namespace"], row["definition_term_name"]) for row in conflicts})
        self.assertTrue(all(len(row["definition_subject_paths"]) == 2 for row in conflicts))


    def test_output_collision_is_reported(self) -> None:
        self.write("001_CORE_META_MODEL", "04_requirement", "SHARED--claim.md", carrier("CA-R-001"))
        self.write("003_PROJECT_CONFIGURATION", "04_requirement", "SHARED--claim.md", carrier("CA-R-002"))
        code, report = self.invoke()
        self.assertEqual(code, 2)
        self.assertIn("output_path_collision", {item["type"] for item in report["conflicts"]})


    def test_dry_run_reports_all_five_conflict_classes(self) -> None:
        self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001-A--one.md", carrier("CA-R-001"))
        self.write("003_PROJECT_CONFIGURATION", "04_requirement", "CA-R-001-B--two.md", carrier("CA-R-001", version=2))
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-002--replacer.md",
            carrier("CA-R-002", relations="\n  replacement_of:\n    - CA-R-003"),
        )
        self.write("003_PROJECT_CONFIGURATION", "04_requirement", "CA-R-003--replaced.md", carrier("CA-R-003"))
        self.write(
            "001_CORE_META_MODEL",
            "04_requirement",
            "CA-R-004--incompatible.md",
            carrier("CA-R-004", relations="\n  incompatible_with:\n    - CA-R-005"),
        )
        self.write("003_PROJECT_CONFIGURATION", "04_requirement", "CA-R-005--other.md", carrier("CA-R-005"))
        self.write(
            "001_CORE_META_MODEL",
            "05_method",
            "CA-M-001--priority-a.md",
            carrier("CA-M-001", extra="applicable_methodology_priority_group: group-one\npriority: 10\n"),
        )
        self.write(
            "003_PROJECT_CONFIGURATION",
            "05_method",
            "CA-M-002--priority-b.md",
            carrier("CA-M-002", extra="applicable_methodology_priority_group: group-one\npriority: 20\n"),
        )
        self.write("001_CORE_META_MODEL", "06_evaluation", "SHARED--collision.md", carrier("CA-E-001"))
        self.write("003_PROJECT_CONFIGURATION", "06_evaluation", "SHARED--collision.md", carrier("CA-E-002"))

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
        for index, directory in enumerate(("draft", "drafts", "archive", "archived", "Draft", "Archived")):
            historical = active.parent / f"copy-{index}" / directory / active.name
            historical.parent.mkdir(parents=True)
            historical.write_bytes(original)
        (self.layers["CORE_META_MODEL"] / "01_concern").mkdir()
        (self.layers["CORE_META_MODEL"] / "01_concern/CA-C-001.md").write_bytes(carrier("CA-C-001"))
        (self.layers["CORE_META_MODEL"] / "08_implementation").mkdir()
        (self.layers["CORE_META_MODEL"] / "08_implementation/CA-I-001.md").write_bytes(carrier("CA-I-001"))
        code, report = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(report["eligible_candidate_count"], 1)
        self.assertEqual(report["conflict_count"], 0)
        self.assertEqual(report["output_plan"][0]["source_carrier_path"], active.relative_to(self.temp).as_posix())
        self.assertEqual(original, active.read_bytes())


    def test_failed_multi_directory_swap_rolls_back(self) -> None:
        self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001--one.md", carrier("CA-R-001"))
        self.write("001_CORE_META_MODEL", "05_method", "CA-M-001--two.md", carrier("CA-M-001"))
        code, _ = self.invoke("--apply")
        self.assertEqual(code, 0)
        output = self.temp / self.output
        before = {path.relative_to(output): path.read_bytes() for path in output.rglob("*.md")}
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
        after = {path.relative_to(output): path.read_bytes() for path in output.rglob("*.md")}
        self.assertEqual(before, after)
