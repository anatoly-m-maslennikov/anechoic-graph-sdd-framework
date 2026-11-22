from __future__ import annotations

from copy import deepcopy
import unittest
from pathlib import Path


from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.project_selection import resolve_project
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_carrier__pub import ScopeDeclarationError
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_declaration_parse__pub import parse_scope_unit_declaration
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests.scope_declaration_render__pub import PROJECT
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.scope_unit_declarations__pub import read_scope_unit_declarations
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__pub import CEILINGS, ReadContext
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.scope_unit_declaration_test_support import ScopeUnitFixture

TOOLS = Path(__file__).resolve().parents[1]


class ScopeUnitDeclarationReaderTests(ScopeUnitFixture, unittest.TestCase):
    def test_prefixed_active_subject_invalid_namespace_chain_refuses(self) -> None:
        source = self.declaration(
            "UNIT", "CA-R-2", scope_id="CA-SU-2", parent=PROJECT, project_name="anechoic",
        )
        source.write_text(source.read_text(encoding="utf-8").replace(
            "ANECHOIC_STRUCTURE <+ Scope Unit//UNIT",
            "ANECHOIC_STRUCTURE {1}<+ Scope Unit//UNIT",
        ), encoding="utf-8")

        with self.assertRaisesRegex(ScopeDeclarationError, "namespace chain"):
            parse_scope_unit_declaration(source.read_bytes(), source)

    def test_project_selection_exposes_derived_structure_and_declaration_provenance(self) -> None:
        self.complete_tree()
        selection = resolve_project(self.root)

        self.assertIn("scope_units", selection.structure)
        self.assertFalse(hasattr(selection, "structure_path"))
        self.assertEqual(len(selection.declaration_paths), 3)
        self.assertEqual(len(selection.declaration_digest), 64)
        self.assertEqual(len(selection.declaration_source_pins), 3)

    def test_deepcopy_retains_one_immutable_declaration_aggregate(self) -> None:
        self.complete_tree()
        declarations = read_scope_unit_declarations(self.root, self.control.name)

        copied = deepcopy({"scope_unit_declarations": declarations})

        self.assertIs(copied["scope_unit_declarations"], declarations)

    def test_draft_archived_generated_and_unrelated_legacy_carriers_are_not_sources(self) -> None:
        self.complete_tree()
        self.declaration(
            "DRAFT", "CA-R-4", source=self.control / "04_requirement" / "draft" / "draft.md",
            scope_id="CA-SU-4", parent=PROJECT,
        )
        self.declaration(
            "ARCHIVED", "CA-R-5", source=self.control / "04_requirement" / "archive" / "archive.md",
            scope_id="CA-SU-5", parent=PROJECT,
        )
        (self.control / "01_concern").mkdir()
        (self.control / "01_concern" / "broken.md").write_text("not an Atom", encoding="utf-8")

        result = read_scope_unit_declarations(self.root, self.control.name)
        self.assertNotIn("DRAFT", result.by_name)
        self.assertNotIn("ARCHIVED", result.by_name)

    def test_ordinary_current_requirement_does_not_conflict_with_declaration_frontier(self) -> None:
        self.complete_tree()
        ordinary = self.control / "04_requirement" / "CA-R-99-ordinary.md"
        ordinary.write_text(
            "---\natom_id: CA-R-99\nrole: Requirement\nform: Policy\nstatus: Active\nversion: 1\n---\n"
            "## Summary\n\nOrdinary Requirement\n",
            encoding="utf-8",
        )
        (self.control / "README.md").write_text("unrelated Markdown", encoding="utf-8")

        result = read_scope_unit_declarations(self.root, self.control.name)
        self.assertEqual(len(result.paths), 3)
        self.assertNotIn(ordinary, result.paths)

    def test_vanished_ordinary_requirement_does_not_block_declaration_discovery(self) -> None:
        self.complete_tree()
        ordinary = self.control / "04_requirement" / "CA-R-99-ordinary.md"
        ordinary.write_text("ordinary", encoding="utf-8")
        reader = ReadContext(roots=[str(self.root)], limits=dict(CEILINGS))
        original_read = reader.read

        def vanish(path: Path, **kwargs) -> bytes:
            if path == ordinary:
                ordinary.unlink()
            return original_read(path, **kwargs)

        reader.read = vanish  # type: ignore[method-assign]

        result = read_scope_unit_declarations(self.root, self.control.name, reader=reader)

        self.assertEqual({"demo", "PARENT", "CHILD"}, set(result.by_name))

    def test_malformed_ordinary_requirement_is_outside_declaration_parser_boundary(self) -> None:
        self.complete_tree()
        ordinary = self.control / "04_requirement" / "CA-R-99-malformed-ordinary.md"
        ordinary.write_text(
            "---\natom_id: CA-R-99\natom_id: CA-R-99\nrole: Requirement\nform: Policy\n---\n",
            encoding="utf-8",
        )

        self.assertEqual(len(read_scope_unit_declarations(self.root, self.control.name).paths), 3)

    def test_malformed_selected_declaration_refuses(self) -> None:
        self.complete_tree()
        malformed = self.control / "04_requirement" / "CA-R-99-malformed-declaration.md"
        malformed.write_text(
            "---\natom_id: CA-R-99\natom_id: CA-R-99\nrole: Requirement\n"
            "form: 'Scope Unit Declaration'\nstatus: Active\nversion: 1\n---\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ScopeDeclarationError, "unique strings"):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_projection_marked_copy_outside_projection_folder_is_not_authority(self) -> None:
        _, _, source = self.complete_tree()
        projected = self.control / "legacyapplied000" / "04_requirement" / "copied-declaration.md"
        projected.parent.mkdir(parents=True)
        projected.write_text(source.read_text(encoding="utf-8").replace(
            "relations: {}",
            "projection:\n  source_carrier_path: ../../CA-SU-1_LAYER_1_PARENT/04_requirement/child.md\nrelations: {}",
        ), encoding="utf-8")

        reader = ReadContext(roots=[str(self.root)], limits=dict(CEILINGS))
        original_read, read_paths = reader.read, []

        def record(path: Path, **kwargs) -> bytes:
            read_paths.append(path)
            return original_read(path, **kwargs)

        reader.read = record  # type: ignore[method-assign]
        result = read_scope_unit_declarations(self.root, self.control.name, reader=reader)
        self.assertEqual(len(result.paths), 3)
        self.assertNotIn(projected, result.paths)
        self.assertNotIn(projected, read_paths)

    def test_root_declaration_is_admitted_only_from_control_top_level(self) -> None:
        root_source, _, _ = self.complete_tree()
        result = read_scope_unit_declarations(self.root, self.control.name)

        self.assertEqual(result.root.source, root_source)
        self.assertEqual(root_source.parent, self.control)

    def test_project_root_declaration_in_requirement_folder_refuses(self) -> None:
        self.declaration("demo", "CA-R-1", project=True)

        with self.assertRaisesRegex(ScopeDeclarationError, "no current Scope Unit Declarations"):
            read_scope_unit_declarations(self.root, self.control.name)

    def test_non_requirement_delegations_use_matching_role_and_parent(self) -> None:
        _, _, child = self.complete_tree()
        raw = child.read_text(encoding="utf-8").replace("form: Scope Unit Declaration", "form: Scope Delegation")
        start = raw.index("### Formal Claim")
        raw = (raw[:start] + "### Prose Claim\n\nDelegated responsibility.\n").replace(
            "---\n", "---\ncontainer:\n  scope_unit: CA-SU-1\n", 1)
        for directory, role, letter in (("05_method", "Method", "M"), ("06_evaluation", "Evaluation", "E"),
                                        ("07_delivery", "Delivery", "D"), ("09_operations", "Operations", "O")):
            with self.subTest(role=role):
                path = child.parent.parent / directory / f"CA-{letter}-4.md"
                path.parent.mkdir()
                carrier = raw.replace("CA-R-3", f"CA-{letter}-4").replace("role: Requirement", f"role: {role}")
                path.write_text(carrier, encoding="utf-8")
                result = read_scope_unit_declarations(self.root, self.control.name)
                self.assertEqual(role, result.by_name["CHILD"].delegations[0].role)
                self.assertIn(path.relative_to(self.root).as_posix(), result.source_pins)
                for invalid in (carrier.replace(f"CA-{letter}-4", "CA-R-4"),
                                carrier.replace("scope_unit: CA-SU-1", "scope_unit: CA-SU-9"),
                                carrier.replace(f"role: {role}", "role: Requirement")):
                    path.write_text(invalid, encoding="utf-8")
                    with self.assertRaises(ScopeDeclarationError):
                        read_scope_unit_declarations(self.root, self.control.name)
                structural = child.read_text(encoding="utf-8").replace("CA-R-3", f"CA-{letter}-4").replace(
                    "role: Requirement", f"role: {role}")
                path.write_text(structural, encoding="utf-8")
                with self.assertRaises(ScopeDeclarationError):
                    read_scope_unit_declarations(self.root, self.control.name)
                path.write_text(structural.replace("form: Scope Unit Declaration", "form: Scope Delegation"), encoding="utf-8")
                with self.assertRaises(ScopeDeclarationError):
                    read_scope_unit_declarations(self.root, self.control.name)
                path.unlink()


if __name__ == "__main__":
    unittest.main()
