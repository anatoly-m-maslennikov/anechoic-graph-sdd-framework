"""Normal startup selects one validated Project across the migration rename."""

from dataclasses import dataclass
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

MCP = Path(__file__).resolve().parents[1]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"
sys.path[:0] = [str(MCP), str(PROGRAMMATIC), str(TOOLS), str(MCP.parents[1] / "IWE_CONSOLE_C43")]

from native_project_selection import NativeProjectSelection
from native_startup import select_runtime_project
from project_selection import ProjectSelectionError
from FEATURE_TOOLS__tests.scope_declaration_test_support import write_scope_unit_declarations


@dataclass
class Manifest:
    name: str
    prefix: str


def validate(fields, owner):
    if owner != "C0" or set(fields) != {"atom_id", "ref_id", "version", "tier", "name", "prefix"}:
        raise ValueError("invalid Manifest")
    return Manifest(fields["name"], fields["prefix"])


def native_fixture_gateway(root, cache, *, selection=None):
    from dataclasses import replace
    from direct_gateway import DirectGateway, startup_selection
    from native_query import NativeQueryOwner
    from native_startup import load_native_inputs

    selected = selection if selection is not None else startup_selection(root)
    inputs = replace(load_native_inputs(selected), extension_directory=cache)
    return DirectGateway(root, native_query=NativeQueryOwner(selected, inputs))


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

    def manifest(self, control, *, name="Anechoic", prefix="AN", component="C0", parameters=None):
        path = control / f"{prefix}-S-001-PROJECT_MANIFEST--declare.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        header = {"identity": {"atom_id": f"{prefix}-S-001"},
                  "context": {"container": {"component": component}, "tier": -1,
                              "template": "project_manifest"},
                  "state": {"status": "active", "version": 1}}
        runtime = f", parameters={parameters!r}" if parameters is not None else ""
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n\n## Claim\n\n### Formal Claim\n\n```python\n"
                        "from anechoic.formal_claims import declare_entity\n"
                        "from anechoic.model import ProjectManifest\n"
                        f"declare_entity(entity_name='Project Manifest', instance=ProjectManifest(name={name!r}, "
                        f"prefix={prefix!r}{runtime}))\n```\n", encoding="utf-8")
        return path

    def select(self, control=None):
        return select_runtime_project(self.root, control, validate_manifest=validate)

    def test_staging_then_final_rename(self):
        old = self.legacy()
        staged = self.root / ".anechoic_new"
        self.manifest(staged)
        with self.assertRaises(ProjectSelectionError):
            self.select()
        old.rename(self.root / ".anechoic_legacy")
        staged.rename(old)
        selected = self.select()
        self.assertIsInstance(selected, NativeProjectSelection)
        self.assertEqual(old, selected.control_root)
        self.assertEqual("AN-S-001@1", selected.manifest_ref)

    def test_legacy_setting_is_ignored_even_when_explicit_native_project_exists(self):
        legacy = self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native)
        with self.assertRaises(ProjectSelectionError):
            self.select(legacy.name)
        self.assertEqual(native, self.select(native.name).control_root)
        self.assertEqual(native, self.select().control_root)

    def test_invalid_native_does_not_fall_back_to_legacy(self):
        self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native, component="bad")
        for control in (native.name, None):
            with self.subTest(control=control), self.assertRaises(ProjectSelectionError):
                self.select(control)

    def test_refuses_legacy_with_manifest_inside_old_spec_directory(self):
        control = self.legacy()
        path = self.manifest(control)
        (control / "SPEC").mkdir()
        path.rename(control / "SPEC" / path.name)
        with self.assertRaises(ProjectSelectionError):
            self.select()

    def test_missing_and_symlink_control_roots_are_refused(self):
        with self.assertRaises(ProjectSelectionError):
            self.select(".anechoic_anechoic")
        (self.root / ".anechoic_anechoic").symlink_to(self.root)
        with self.assertRaises(ProjectSelectionError):
            self.select(".anechoic_anechoic")

    def test_project_settings_do_not_shadow_native_manifest(self):
        control = self.legacy()
        self.manifest(control)
        for explicit in (control.name, None):
            with self.subTest(explicit=explicit):
                self.assertEqual(control, self.select(explicit).control_root)

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

    def test_refuses_two_native_manifests_and_ignores_retained_legacy(self):
        self.manifest(self.root / ".anechoic_anechoic")
        self.manifest(self.root / ".anechoic_other", name="Other", prefix="OT")
        with self.assertRaisesRegex(ProjectSelectionError, "unique native Project Manifest"):
            self.select()
        (self.root / ".anechoic_other" / "OT-S-001-PROJECT_MANIFEST--declare.md").unlink()
        self.legacy(".anechoic_legacy", declared=".anechoic_unknown")
        self.assertEqual(self.root / ".anechoic_anechoic", self.select().control_root)


if __name__ == "__main__":
    unittest.main()
