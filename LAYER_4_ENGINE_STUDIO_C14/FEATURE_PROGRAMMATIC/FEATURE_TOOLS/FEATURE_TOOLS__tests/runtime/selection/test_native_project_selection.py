"""Explicit binding uses the Manifest and preserves legacy discovery."""

import ast
from datetime import datetime
from hashlib import sha256
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str((TOOLS := Path(__file__).resolve().parents[3]).parent))
sys.path.insert(0, str(TOOLS))

# fmt: off
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.FEATURE_PROJECT_TOOLS__tests \
    .FEATURE_PROJECT_TOOLS__tests__shared import (  # noqa: E402
        validate_manifest,
        write_scope_unit_declarations,
    )
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    discover_native_project,
    resolve_native_project,
    resolve_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (  # noqa: E402
    CEILINGS,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.settings.project.project_manifest__pub import (  # noqa: E402
    ProjectSelectionError,
)
# fmt: on
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.runtime.selection import (
    native_selection_support as support,
)  # noqa: E402


class ManifestReaderBoundaryTests(unittest.TestCase):
    def test_reader_imports_only_standard_library_and_c30(self):
        path = TOOLS / "ADAPTERS_C30" / "settings/project/project_manifest__pub.py"
        imports = [
            node
            for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node, (ast.Import, ast.ImportFrom))
        ]
        for node in imports:
            if isinstance(node, ast.ImportFrom):
                self.assertTrue(
                    0 < node.level <= 3
                    or node.module in {"datetime", "pathlib"}
                    or (node.module or "").startswith(
                        "FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30."
                    )
                )
            else:
                self.assertEqual([alias.name for alias in node.names], ["re"])


class NativeProjectSelectionTests(
    support.NativeSelectionFixture,
    support.NativeSelectionParameterCases,
    unittest.TestCase,
):
    def explicit_binding_preserves_legacy_coexistence(self):
        legacy = self.root / ".anechoic_legacy"
        legacy.mkdir()
        (legacy / "anechoic_project_settings.toml").write_text(
            '[project]\nname="legacy"\nkey="legacy"\n'
            'repository_slug="legacy"\n'
            '[paths]\ncontrol_root=".anechoic_legacy"\n'
            '[artifacts.identity]\nproject_prefix="CA"\n',
            encoding="utf-8",
        )
        write_scope_unit_declarations(self.root, control_root=legacy)
        active = self.carrier()
        for area in (
            "_PMETA",
            "__TKT",
            "draft",
            "archived",
            "archive",
            "SPEC/subsection",
        ):
            self.carrier(f"{area}/{active.name}")
        native = self.select()
        self.assertEqual(
            ("Anechoic", "AN", self.native),
            (native.project_name, native.project_prefix, native.control_root),
        )
        self.assertEqual(
            (active, "AN-S-001@3", sha256(active.read_bytes()).hexdigest()),
            (
                native.manifest_path,
                native.manifest_ref,
                native.manifest_sha256,
            ),
        )
        legacy_default = resolve_project(self.root)
        self.assertEqual(legacy, legacy_default.control_root)
        self.assertNotEqual(legacy_default.instance_id, native.instance_id)
        self.assertFalse((self.root / ".anechoic_runtime").exists())

    def test_root_manifest_takes_precedence_and_discovery_infers_control(self):
        legacy = self.carrier()
        root_manifest = legacy.rename(self.root / legacy.name)
        self.carrier(name="Other")
        (self.root / "README.md").write_text("unrelated content")
        selected = self.select()
        self.assertEqual(root_manifest, selected.manifest_path)
        self.assertEqual(
            root_manifest,
            discover_native_project(
                self.root, manifest_validator=lambda: validate_manifest
            ).manifest_path,
        )

    def test_root_component_manifest_preserves_project_fields(self):
        path = self.carrier()
        root_manifest = path.rename(self.root / path.name)
        header = root_manifest.read_text().split("## Claim", 1)[0]
        root_manifest.write_text(
            header + "## Formal Manifest\n\n```python anechoic-edsl\n"
            "from anechoic.model import ComponentManifest\n"
            "ComponentManifest(name='Anechoic', prefix='AN', "
            "lens_whitelist=['SPEC'], parameters={"
            "'root': {'prefix': 'dot'}, "
            "'project_mcp': {'inline_result_limit_kib': 8}, "
            "'runtime': {'journal.storage': 'duckdb', "
            "'duck_db.storage': 'disk'}})\n```\n",
            encoding="utf-8",
        )
        selected = self.select()
        self.assertEqual(root_manifest, selected.manifest_path)
        self.assertEqual("Anechoic", selected.project_name)
        self.assertEqual("AN", selected.project_prefix)
        self.assertEqual(
            {
                "journal": {"storage": "duckdb"},
                "iwe_console": {
                    "storage": "disk",
                    "inline_result_limit_kib": 8,
                },
            },
            selected.parameters["runtime"],
        )
        self.assertEqual(
            {"prefix": "dot"}, selected.parameters["project"]["root"]
        )

    def test_root_candidate_refuses_bad_or_duplicate_and_does_not_fall_back(
        self,
    ):
        legacy = self.carrier()
        root_manifest = self.root / legacy.name
        root_manifest.write_text("---\ninvalid: [\n---\n")
        with self.assertRaises(ProjectSelectionError):
            self.select()
        root_manifest.write_text(
            legacy.read_text().replace("status: active", "status: draft")
        )
        with self.assertRaises(ProjectSelectionError):
            self.select()
        root_manifest.write_text(legacy.read_text())
        second = self.carrier(
            "AN-S-002-PROJECT_MANIFEST--declare-anechoic.md",
            atom_id="AN-S-002",
        )
        second.rename(self.root / second.name)
        with self.assertRaises(ProjectSelectionError):
            self.select()

    def test_root_manifest_requires_safe_existing_control(self):
        legacy = self.carrier()
        legacy.rename(self.root / legacy.name)
        self.native.rmdir()
        with self.assertRaises(ProjectSelectionError):
            self.select()

    def test_canonical_manifest_header(self):
        path = self.carrier()
        text = path.read_text()
        _, header, body = text.split("---", 2)
        metadata = yaml.safe_load(header)
        metadata["atom_family"] = "SPEC"
        metadata["atom_id"] = metadata.pop("identity")["atom_id"]
        metadata["structure"] = {
            "container": metadata["context"].pop("container"),
            "tier": metadata["context"].pop("tier"),
        }
        path.write_text(f"---\n{yaml.safe_dump(metadata)}---{body}")
        self.assertEqual("AN-S-001@3", self.select().manifest_ref)

    def test_refuses_missing_and_ambiguous_active_manifest(self):
        self.carrier(status="draft")
        with self.assertRaisesRegex(
            ProjectSelectionError, "Expected one Active"
        ):
            self.select()
        self.carrier()
        self.carrier(
            "AN-S-002-PROJECT_MANIFEST--declare-anechoic.md",
            atom_id="AN-S-002",
        )
        with self.assertRaisesRegex(
            ProjectSelectionError, "Expected one Active"
        ):
            self.select()

    def test_passes_authored_state_to_strict_model(self):
        path = self.carrier()
        header = path.read_text()

        def check(fields, component_id):
            fields = dict(fields)
            self.assertEqual("active", fields.pop("status"))
            self.assertEqual(
                datetime.fromisoformat("2026-11-19T00:00:00Z"),
                fields.pop("updated_at"),
            )
            return validate_manifest(fields, component_id)

        def select():
            return resolve_native_project(
                self.root,
                self.native.name,
                validate_manifest=check,
                require_atom_state=True,
            )

        select()
        timestamp_line = next(
            line
            for line in header.splitlines(keepends=True)
            if line.startswith("  updated_at:")
        )
        for bad in ("", "  updated_at: invalid\n"):
            path.write_text(header.replace(timestamp_line, bad))
            with self.assertRaises(ProjectSelectionError):
                select()

    def test_old_spec_directory_is_ignored_and_never_walked(self):
        self.carrier("SPEC/AN-S-001-PROJECT_MANIFEST--declare-anechoic.md")
        with self.assertRaisesRegex(
            ProjectSelectionError, "Expected one Active"
        ):
            self.select()
        self.carrier()
        (self.native / "SPEC" / "unreadable-link").symlink_to(
            self.root / "missing"
        )
        self.assertEqual(
            self.native / "AN-S-001-PROJECT_MANIFEST--declare-anechoic.md",
            self.select().manifest_path,
        )

    def test_refuses_manifest_added_during_native_validation(self):
        self.carrier()

        def add_manifest(fields, component):
            self.carrier(
                "AN-S-002-PROJECT_MANIFEST--declare-anechoic.md",
                atom_id="AN-S-002",
            )
            return validate_manifest(fields, component)

        with self.assertRaisesRegex(
            ProjectSelectionError, "changed during selection"
        ):
            resolve_native_project(
                self.root, self.native.name, validate_manifest=add_manifest
            )

    def test_direct_root_inventory_is_bounded(self):
        self.carrier()
        (self.native / "one").touch()
        (self.native / "two").touch()
        with (
            patch.dict(CEILINGS, {"max_candidates": 2}),
            self.assertRaises(ProjectSelectionError),
        ):
            self.select()

    def test_passes_the_authored_lens_whitelist_to_typed_validation(self):
        for lenses in ([], ["SPEC"]):
            with self.subTest(lenses=lenses):
                self.carrier(lens_whitelist=lenses)

                def check(fields, component_id):
                    manifest = validate_manifest(fields, component_id)
                    self.assertEqual(lenses, manifest.lens_whitelist)
                    return manifest

                resolve_native_project(
                    self.root, self.native.name, validate_manifest=check
                )

    def test_refuses_contradictory_identity_and_invalid_owner(self):
        for values, error in (
            ({"name": "other"}, "name contradicts"),
            ({"prefix": "XX"}, "prefix contradicts"),
            ({"tier": 0}, "Invalid Active"),
            ({"component": "C43"}, "invalid, or unsafe"),
        ):
            with (
                self.subTest(values=values),
                self.assertRaisesRegex(ProjectSelectionError, error),
            ):
                self.carrier(**values)
                self.select()

    def test_refuses_symlink_manifest(self):
        outside = self.carrier()
        renamed = outside.rename(self.root / "outside.md")
        outside.symlink_to(renamed)
        with self.assertRaisesRegex(
            ProjectSelectionError, "invalid, or unsafe"
        ):
            self.select()


setattr(
    NativeProjectSelectionTests,
    "test_explicit_binding_pins_one_native_manifest_during_legacy_coexistence",
    NativeProjectSelectionTests.explicit_binding_preserves_legacy_coexistence,
)


if __name__ == "__main__":
    unittest.main()
