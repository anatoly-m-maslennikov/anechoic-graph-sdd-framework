"""Normal startup selects one validated Project across the migration rename."""

from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(TOOLS), str(MCP.parents[1] / "IWE_CONSOLE_C43")]

from native_project_selection import NativeProjectSelection
from native_startup import select_runtime_project
from project_selection import ProjectSelection, ProjectSelectionError, resolve_project
from scope_declaration_test_support import write_scope_unit_declarations


@dataclass
class Manifest:
    name: str
    prefix: str


def validate(fields, owner):
    if owner != "C0" or set(fields) != {"atom_id", "ref_id", "version", "tier", "name", "prefix"}:
        raise ValueError("invalid Manifest")
    return Manifest(fields["name"], fields["prefix"])


class RuntimeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()

    def legacy(self, name=".anechoic_anechoic", declared=None):
        control = self.root / name
        control.mkdir()
        (control / "anechoic_project_settings.toml").write_text(
            '[project]\nname="Anechoic"\nkey="anechoic"\nrepository_slug="anechoic"\n'
            f'[paths]\ncontrol_root="{declared or name}"\n[artifacts.identity]\nproject_prefix="CA"\n',
            encoding="utf-8",
        )
        write_scope_unit_declarations(self.root, control_root=control)
        return control

    def manifest(self, control, *, name="Anechoic", prefix="AN", component="C0"):
        path = control / "SPEC" / f"{prefix}-S-001-PROJECT_MANIFEST--declare.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": f"{prefix}-S-001"},
                  "context": {"container": {"component": component}, "tier": -1,
                              "template": "project_manifest"},
                  "state": {"status": "active", "version": 1}}
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n## Claim\n\n### Formal Claim\n\n```python\n"
                        "from anechoic.formal_claims import declare_entity\n"
                        "from anechoic.model import ProjectManifest\n"
                        f"declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name={name!r}, "
                        f"prefix={prefix!r}))\n```\n", encoding="utf-8")
        return path

    def select(self, control=None):
        return select_runtime_project(self.root, control, validate_manifest=validate)

    def test_staging_then_final_rename(self):
        old = self.legacy()
        staged = self.root / ".anechoic_new"
        self.manifest(staged)
        self.assertIsInstance(self.select(), ProjectSelection)
        self.assertEqual(old, self.select().control_root)
        self.assertEqual(old, resolve_project(self.root).control_root)
        old.rename(self.root / ".anechoic_legacy")
        staged.rename(old)
        selected = self.select()
        self.assertIsInstance(selected, NativeProjectSelection)
        self.assertEqual(old, selected.control_root)
        self.assertEqual("AN-S-001@1", selected.manifest_ref)
        with self.assertRaises(ProjectSelectionError):
            resolve_project(self.root)

    def test_explicit_legacy_and_native(self):
        legacy = self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native)
        self.assertEqual(legacy, self.select(legacy.name).control_root)
        self.assertEqual(native, self.select(native.name).control_root)
        with self.assertRaisesRegex(ProjectSelectionError, "ambiguous"):
            self.select()

    def test_invalid_native_does_not_fall_back_to_legacy(self):
        self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native, component="bad")
        for control in (native.name, None):
            with self.subTest(control=control), self.assertRaises(ProjectSelectionError):
                self.select(control)

    def test_refuses_manifest_added_during_legacy_selection(self):
        control = self.legacy()

        def resolve_then_add(*args, **kwargs):
            selection = resolve_project(*args, **kwargs)
            self.manifest(control)
            return selection

        with patch("native_startup.resolve_project", side_effect=resolve_then_add):
            with self.assertRaisesRegex(ProjectSelectionError, "changed during selection"):
                self.select(control.name)

    def test_both_formats_in_one_root_are_ambiguous(self):
        control = self.legacy()
        self.manifest(control)
        for explicit in (control.name, None):
            with self.subTest(explicit=explicit), self.assertRaisesRegex(ProjectSelectionError, "ambiguous"):
                self.select(explicit)

    def test_default_model_validates_native_selection(self):
        self.manifest(self.root / ".anechoic_anechoic", component="C00")
        selection = select_runtime_project(self.root)
        self.assertEqual("AN-S-001@1", selection.manifest_ref)

    def test_malformed_manifest_does_not_select_legacy_in_same_control(self):
        control = self.legacy()
        self.manifest(control).write_text("---\n[invalid", encoding="utf-8")
        for explicit in (control.name, None):
            with self.subTest(explicit=explicit), self.assertRaises(ProjectSelectionError):
                self.select(explicit)

    def test_discovery_rejects_excessive_control_roots(self):
        for index in range(65):
            (self.root / f".anechoic_candidate{index}").mkdir()
        with self.assertRaisesRegex(ProjectSelectionError, "ceiling"):
            self.select()

    def test_staging_is_never_discovered_implicitly(self):
        self.manifest(self.root / ".anechoic_new")
        with self.assertRaises(ProjectSelectionError):
            self.select()

    def test_native_ambiguity_and_unrelated_invalid_legacy_are_refused(self):
        self.manifest(self.root / ".anechoic_anechoic")
        self.manifest(self.root / ".anechoic_other", name="Other", prefix="OT")
        with self.assertRaisesRegex(ProjectSelectionError, "ambiguous"):
            self.select()
        (self.root / ".anechoic_other" / "SPEC" / "OT-S-001-PROJECT_MANIFEST--declare.md").unlink()
        self.legacy(".anechoic_legacy", declared=".anechoic_unknown")
        with self.assertRaises(ProjectSelectionError):
            self.select()


if __name__ == "__main__":
    unittest.main()
