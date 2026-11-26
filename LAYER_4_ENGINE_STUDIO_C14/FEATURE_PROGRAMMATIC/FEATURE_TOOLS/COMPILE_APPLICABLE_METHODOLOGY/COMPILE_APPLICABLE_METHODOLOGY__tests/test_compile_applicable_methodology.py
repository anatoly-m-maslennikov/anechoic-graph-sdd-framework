"""Applicable Methodology compilation behavior."""

import os
from pathlib import Path

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.COMPILE_APPLICABLE_METHODOLOGY__tests.methodology_test_support import (
    CompilerFixture, module, carrier, term_definition_carrier,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.COMPILE_APPLICABLE_METHODOLOGY.methodology_paths__shared import declaration_source_pins


class CompilerTest(CompilerFixture):
    def test_retired_cce_form_does_not_define_a_term(self) -> None:
        frontmatter = 'cce_form: definition\nsubjects:\n  governs: "Old Term"\n'
        self.assertEqual((None, None, ""), module.definition_subject(frontmatter, "test.md"))
        frontmatter = 'cce_form: definition\nrole: Method\nform: Term Definition\ntopics:\n  main_subject: Term//Current Term\n'
        self.assertEqual(("Current Term", "Term//Current Term", ""),
                         module.definition_subject(frontmatter, "test.md"))


    def test_current_term_definition_requires_a_flat_term_subject(self) -> None:
        for subject in ("", "Term", "Entity//Shared Term", "Term//Shared Term/Other",
                        "ANECHOIC_STRUCTURE <+ Term//Shared Term"):
            with self.subTest(subject=subject):
                frontmatter, _ = module.split_frontmatter(term_definition_carrier("CA-M-010", subject), "test.md")
                with self.assertRaises(module.CompileError) as error:
                    module.definition_subject(frontmatter, "test.md")
                self.assertEqual("source-subject-path-invalid", error.exception.code)

        self.assertEqual(
            (None, None, ""),
            module.definition_subject("role: Requirement\nform: Rule\ntopics:\n  main_subject: Term//Shared Term\n", "test.md"),
        )


    def test_term_definition_preserves_model_identity(self) -> None:
        for subject in ("Term//ID", "ANECHOIC_MODEL <+ Term//ID", "MODEL//ANECHOIC <+ Term//ID",
                        "ANECHOIC <+ MODEL <+ Term//ID"):
            with self.subTest(subject=subject):
                frontmatter, _ = module.split_frontmatter(term_definition_carrier("CA-M-010", subject), "test.md")
                self.assertEqual(("ID", subject, ""), module.definition_subject(frontmatter, "test.md"))
        subject = "MODEL//Other <+ Term//ID"
        frontmatter, _ = module.split_frontmatter(term_definition_carrier("CA-M-010", subject), "test.md")
        self.assertEqual(("ID", subject, "MODEL//Other"), module.definition_subject(frontmatter, "test.md"))


    def test_identity_is_independent_of_mutable_filename_tokens(self) -> None:
        for name in (
            "CA-M-120-GOVERN-CORE-METHOD--old.md",
            "CA-M-120-CORE_META_MODEL-CORE-METHOD--new.md",
            "03-CA-M-120-CORE_META_MODEL-METHOD--new.md",
        ):
            self.assertEqual("CA-M-120", module.derive_atom_id(Path(name), "version: 1"))
        self.assertEqual(
            "ANECHOIC-E-169-EVAL_APPROACH",
            module.derive_atom_id(Path("ANECHOIC-E-169-CORE-EVAL_APPROACH--new.md"),
                                 'atom_id: "ANECHOIC-E-169-EVAL_APPROACH"'),
        )


    def test_dry_run_apply_rerun_and_regeneration_are_deterministic(self) -> None:
        source = self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001-REQUIREMENT--one.md", carrier("CA-R-001"))
        local = self.write("003_PROJECT_CONFIGURATION", "05_method", "CA-M-001-METHOD--two.md", carrier("CA-M-001", body="two"))
        before = {source: source.read_bytes(), local: local.read_bytes()}

        first_code, first = self.invoke()
        second_code, second = self.invoke()
        self.assertEqual((first_code, first), (0, second))
        self.assertEqual(first["conflict_count"], 0)

        apply_code, applied = self.invoke("--apply")
        self.assertEqual(apply_code, 0)
        first_tree = self.output_digest()
        self.assertEqual(before, {source: source.read_bytes(), local: local.read_bytes()})
        projected = self.temp / self.output / "04_requirement" / source.name
        projected_text = projected.read_text()
        self.assertIn(
            f"projection:\n  source_carrier_path: {Path(os.path.relpath(source, start=projected.parent)).as_posix()}",
            projected_text,
        )
        self.assertIn("# CA-R-001\n\nclaim", projected_text)

        rerun_code, rerun = self.invoke("--apply")
        self.assertEqual(rerun_code, 0)
        self.assertEqual(first_tree, self.output_digest())

        for _, role in module.ROLES:
            for path in (self.temp / self.output / role).glob("*"):
                path.unlink()
        regenerate_code, regenerated = self.invoke("--apply")
        self.assertEqual(regenerate_code, 0)
        self.assertEqual(first_tree, self.output_digest())
        self.assertEqual(before, {source: source.read_bytes(), local: local.read_bytes()})


    def test_nested_header_compiles_alongside_flat_source_without_rewriting_either(self) -> None:
        nested = (
            b"---\nidentity:\n  atom_id: CA-R-001\n  ref_id: CA-R-001@2\n"
            b"context:\n  role: Requirement\n  form: Rule\n  topics:\n    main_subject: Header\n    dependencies: []\n"
            b"relations: {}\nstate:\n  status: Active\n  version: 2\n"
            b'  updated_at: "2026-11-06 00:00:00 +0400"\n'
            b"destination:\n  file:\n    name: CA-R-001--nested\n    path: preserved/path\n"
            b"---\n# Claim\n\nExact nested source body.\n"
        )
        source = self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001--nested.md", nested)
        flat = self.write("003_PROJECT_CONFIGURATION", "05_method", "CA-M-001--flat.md", carrier("CA-M-001"))
        before = {source: nested, flat: flat.read_bytes()}
        candidates, diagnostics, _ = module.discover_candidates(self.temp)
        self.assertFalse(diagnostics)
        self.assertEqual({"CA-R-001": 2, "CA-M-001": 1}, {row.atom_id: row.version for row in candidates})

        code, report = self.invoke("--apply")
        self.assertEqual(0, code, report)
        projected = self.temp / self.output / "04_requirement" / source.name
        candidate = next(row for row in candidates if row.atom_id == "CA-R-001")
        relative = Path(os.path.relpath(source, start=projected.parent)).as_posix()
        module.validate_projection_source_preservation(nested, projected.read_bytes(), relative, candidate)
        self.assertEqual(before, {path: path.read_bytes() for path in before})


    def test_flat_active_status_encodings_are_selected(self) -> None:
        for number, status in enumerate(("Active", "active", "Draft", "ACTIVE"), start=1):
            atom_id = f"CA-R-{number:03d}"
            raw = carrier(atom_id).replace(b"status: Active\n", f"status: {status}\n".encode())
            self.write("001_CORE_META_MODEL", "04_requirement", f"{atom_id}--status.md", raw)

        candidates, diagnostics, _ = module.discover_candidates(self.temp)

        self.assertEqual({"CA-R-001", "CA-R-002"}, {row.atom_id for row in candidates})
        self.assertEqual({"Draft", "ACTIVE"}, {row["status"] for row in diagnostics})
        self.assertTrue(all(row["reason"] == "inactive" for row in diagnostics))


    def test_conflicting_flat_and_nested_state_is_a_source_diagnostic(self) -> None:
        raw = carrier("CA-R-001").replace(b"status: Active\n", b"status: Active\nstate:\n  status: Draft\n")
        source = self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001--conflict.md", raw)
        candidates, diagnostics, _ = module.discover_candidates(self.temp)
        self.assertFalse(candidates)
        self.assertIn("source-frontmatter-invalid", {row["code"] for row in diagnostics})
        self.assertEqual(raw, source.read_bytes())


    def test_ignores_ds_store_in_source_snapshot(self) -> None:
        self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001--one.md", carrier("CA-R-001"))
        places = module.methodology_paths(self.temp)
        snapshot = module.source_state_snapshot(self.temp, places)

        (self.layers["CORE_META_MODEL"] / ".DS_Store").write_bytes(b"finder metadata")
        (self.layers["PROJECT_CONFIGURATION"] / ".DS_Store").write_bytes(b"finder metadata")

        self.assertEqual(snapshot, module.source_state_snapshot(self.temp, places))
        self.assertEqual(snapshot, module.source_state_snapshot(self.temp, places))


    def test_source_unit_role_directories_do_not_count_as_source_layers(self) -> None:
        (self.source / "04_requirement").mkdir(exist_ok=True)
        (self.source / "04_requirement/CA-R-100--define-source-layer-goal.md").write_bytes(carrier("CA-R-100"))
        self.write("001_CORE_META_MODEL", "04_requirement", "CA-R-001--one.md", carrier("CA-R-001"))

        code, report = self.invoke()

        self.assertEqual(code, 0)
        self.assertTrue(report["can_apply"])
        self.assertEqual(report["selected_candidate_count"], 1)


    def test_declarations_drive_configured_projection_places(self) -> None:
        places = module.methodology_paths(self.temp)

        self.assertEqual(self.source.relative_to(self.temp), places.source)
        self.assertEqual(self.output.relative_to(self.temp), places.output)
        self.assertIn(
            self.declarations["METHODOLOGY_SOURCES"]["declaration_path"].relative_to(self.temp).as_posix(),
            declaration_source_pins(self.temp, places),
        )


    def test_changed_declaration_frontier_blocks_staging_at_original_places(self) -> None:
        self.write("001_CORE_META_MODEL", "05_method", "CA-M-001--one.md", carrier("CA-M-001"))
        places = module.methodology_paths(self.temp)
        _, candidates, snapshot = module.compile_report(self.temp, places)
        declaration = Path(self.declarations["METHODOLOGY_SOURCES"]["declaration_path"])
        declaration.write_text(declaration.read_text(encoding="utf-8").replace("2026-11-02", "2026-11-03"), encoding="utf-8")

        with self.assertRaises(module.CompileError) as raised:
            module.stage_outputs(self.temp, candidates, snapshot, places)

        self.assertEqual("source-frontier-changed", raised.exception.code)
        self.assertFalse((self.temp / self.output).exists())
