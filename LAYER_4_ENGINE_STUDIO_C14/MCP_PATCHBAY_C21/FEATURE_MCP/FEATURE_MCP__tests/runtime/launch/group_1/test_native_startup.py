"""Normal startup selects one validated Project across the migration rename."""

from ....native_query_test_support import local_gateway
from ....FEATURE_MCP__tests__shared import write_manifest


from pathlib import Path
import tempfile
import unittest


from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
    ProjectAdmissionError,
    ProjectBinding,
    project_admission,
    select_runtime_project,
)
from FEATURE_PROGRAMMATIC.FEATURE_PROJECT_TOOLS.\
    FEATURE_PROJECT_TOOLS__tests.FEATURE_PROJECT_TOOLS__tests__shared import (
    write_scope_unit_declarations,
)  # fmt: skip

MCP = Path(__file__).resolve().parents[4]
PROGRAMMATIC = MCP.parents[1] / "FEATURE_PROGRAMMATIC"
TOOLS = PROGRAMMATIC / "FEATURE_TOOLS"


def native_fixture_gateway(root, cache, *, selection=None):
    from dataclasses import asdict, replace
    from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.PROJECT_SUPPORT.\
        PROJECT_SELECTION.PROJECT_SELECTION__shared import (
        NativeProjectSelection,
    )
    from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
        select_runtime_project as startup_selection,
    )
    from KERNEL_MIXER_C59.KERNEL_MIXER_C59__shared import NativeQueryOwner
    from ....native_query_test_support import load_native_inputs

    fields = asdict(
        selection if selection is not None else startup_selection(root)
    )
    fields.pop("tool_blacklist", None)
    fields.pop("release_workflows_enabled", None)
    selected = NativeProjectSelection(**fields)
    inputs = replace(load_native_inputs(selected), extension_directory=cache)
    return local_gateway(root, native_query=NativeQueryOwner(selected, inputs))


class RuntimeSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.admit = cls.enterClassContext(project_admission())

    def setUp(self):
        self.root = Path(
            self.enterContext(tempfile.TemporaryDirectory())
        ).resolve()

    def legacy(self, name=".anechoic_anechoic", declared=None):
        control = self.root / name
        control.mkdir()
        (control / "anechoic_project_settings.toml").write_text(
            '[project]\nname="Anechoic"\nkey="anechoic"\n'
            'repository_slug="anechoic"\n'
            f'[paths]\ncontrol_root="{declared or name}"\n'
            '[artifacts.identity]\nproject_prefix="CA"\n',
            encoding="utf-8",
        )
        write_scope_unit_declarations(self.root, control_root=control)
        return control

    manifest = write_manifest

    def select(self, control=None):
        return self.admit(self.root, control)

    def test_staging_then_final_rename(self):
        old = self.legacy()
        staged = self.root / ".anechoic_new"
        self.manifest(staged)
        with self.assertRaises(ProjectAdmissionError):
            self.select()
        old.rename(self.root / ".anechoic_legacy")
        staged.rename(old)
        selected = self.select()
        self.assertIsInstance(selected, ProjectBinding)
        self.assertEqual(old, selected.control_root)
        self.assertEqual("AN-S-001@1", selected.manifest_ref)

    # fmt: off
    def \
    test_legacy_setting_is_ignored_even_when_explicit_native_project_exists(
        self,
    ):
        # fmt: on
        legacy = self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native)
        with self.assertRaises(ProjectAdmissionError):
            self.select(legacy.name)
        self.assertEqual(native, self.select(native.name).control_root)
        self.assertEqual(native, self.select().control_root)

    def test_invalid_native_does_not_fall_back_to_legacy(self):
        self.legacy(".anechoic_legacy")
        native = self.root / ".anechoic_anechoic"
        self.manifest(native, component="bad")
        for control in (native.name, None):
            with (
                self.subTest(control=control),
                self.assertRaises(ProjectAdmissionError),
            ):
                self.select(control)

    def test_refuses_legacy_with_manifest_inside_old_spec_directory(self):
        control = self.legacy()
        path = self.manifest(control)
        (control / "SPEC").mkdir()
        path.rename(control / "SPEC" / path.name)
        with self.assertRaises(ProjectAdmissionError):
            self.select()

    def test_missing_and_symlink_control_roots_are_refused(self):
        with self.assertRaises(ProjectAdmissionError):
            self.select(".anechoic_anechoic")
        (self.root / ".anechoic_anechoic").symlink_to(self.root)
        with self.assertRaises(ProjectAdmissionError):
            self.select(".anechoic_anechoic")

    def test_project_settings_do_not_shadow_native_manifest(self):
        control = self.legacy()
        self.manifest(control)
        for explicit in (control.name, None):
            with self.subTest(explicit=explicit):
                self.assertEqual(control, self.select(explicit).control_root)

    def test_reusable_admission_selects_current_pins_without_opening_workbench(
        self,
    ):
        alpha, beta = self.root / "alpha", self.root / "beta"
        first_manifest = self.manifest(
            alpha / ".anechoic_alpha",
            name="Alpha",
            prefix="AL",
            component="C00",
        )
        self.manifest(
            beta / ".anechoic_beta",
            name="Beta",
            prefix="BE",
            component="C00",
            parameters={
                "project_mcp": {
                    "tool_blacklist": ["query_schema"],
                    "release_workflows_enabled": True,
                }
            },
        )
        with project_admission() as select:
            first = select(alpha)
            other = select(beta)
            self.assertEqual((alpha, beta), (first.root, other.root))
            self.assertNotEqual(first.instance_id, other.instance_id)
            self.assertEqual(("query_schema",), other.tool_blacklist)
            self.assertTrue(other.release_workflows_enabled)
            with self.assertRaises(ProjectAdmissionError):
                select(alpha, instance_id="0" * 64, host_root=alpha)
            first_manifest.write_text(
                first_manifest.read_text(encoding="utf-8").replace(
                    "version: 1", "version: 2", 1
                ),
                encoding="utf-8",
            )
            revised = select(alpha)
            self.assertEqual("AL-S-001@2", revised.manifest_ref)
            self.assertNotEqual(first.manifest_sha256, revised.manifest_sha256)
            self.assertEqual(other, select(beta))
        for root in (alpha, beta):
            self.assertFalse(
                (root / ".anechoic_runtime/db/project.duckdb").exists()
            )

    def test_family_selection_is_accepted_by_native_gateway(self):
        from MCP_PATCHBAY_C21.FEATURE_MCP.FEATURE_MCP__shared import (
            select_runtime_project as family_select,
        )
        from MCP_PATCHBAY_C21.FEATURE_MCP.gateway.gateway__shared import (
            native_project_gateway,
        )

        self.manifest(self.root / ".anechoic_anechoic")
        selected = family_select(self.root)
        gateway = native_project_gateway(self.root, selection=selected)
        self.assertIs(gateway.selection, selected)
        self.assertIsInstance(selected, ProjectBinding)

    def test_default_model_validates_native_selection(self):
        self.manifest(self.root / ".anechoic_anechoic", component="C00")
        selection = select_runtime_project(self.root)
        self.assertEqual("AN-S-001@1", selection.manifest_ref)

    def test_malformed_manifest_does_not_select_legacy_in_same_control(self):
        control = self.legacy()
        self.manifest(control).write_text("---\n[invalid", encoding="utf-8")
        for explicit in (control.name, None):
            with (
                self.subTest(explicit=explicit),
                self.assertRaises(ProjectAdmissionError),
            ):
                self.select(explicit)

    def test_discovery_rejects_excessive_control_roots(self):
        for index in range(65):
            (self.root / f".anechoic_candidate{index}").mkdir()
        with self.assertRaisesRegex(ProjectAdmissionError, "ceiling"):
            self.select()

    def test_visible_control_is_discovered_and_ambiguous_with_hidden_control(
        self,
    ):
        visible = self.root / "_anechoic_anechoic"
        self.manifest(visible)
        self.assertEqual(visible, self.select().control_root)
        self.assertEqual(visible, self.select(visible.name).control_root)
        self.manifest(self.root / ".anechoic_anechoic")
        with self.assertRaisesRegex(
            ProjectAdmissionError, "unique native Project Manifest"
        ):
            self.select()

    def test_visible_symlink_candidate_is_refused(self):
        (self.root / "_anechoic_anechoic").symlink_to(self.root)
        with self.assertRaises(ProjectAdmissionError):
            self.select()

    def test_staging_is_never_discovered_implicitly(self):
        self.manifest(self.root / ".anechoic_new")
        with self.assertRaises(ProjectAdmissionError):
            self.select()

    def test_refuses_two_native_manifests_and_ignores_retained_legacy(self):
        self.manifest(self.root / ".anechoic_anechoic")
        self.manifest(self.root / ".anechoic_other", name="Other", prefix="OT")
        with self.assertRaisesRegex(
            ProjectAdmissionError, "unique native Project Manifest"
        ):
            self.select()
        (
            self.root
            / ".anechoic_other"
            / "OT-S-001-PROJECT_MANIFEST--declare.md"
        ).unlink()
        self.legacy(".anechoic_legacy", declared=".anechoic_unknown")
        self.assertEqual(
            self.root / ".anechoic_anechoic", self.select().control_root
        )


if __name__ == "__main__":
    unittest.main()
