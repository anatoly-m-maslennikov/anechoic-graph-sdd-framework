import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import NonCallableMock

import yaml

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.sources.inventory.inventory__shared import (
    capture_native,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.model.model_capture import model_inputs
from ..LAYER_2_PROJECT_STRUCTURE_C93__rows import (
    StructureAdmissionError,
    compile_structure_rows,
)
from ..LAYER_2_PROJECT_STRUCTURE_C93__shared import compile_structure
from .structure_fixtures import (
    CANONICAL_BODY,
    COMPONENT,
    LEGACY_COMPONENT,
    PROJECT,
    Model,
    StructureFixture,
    selection,
)


class StructureTests(StructureFixture, unittest.TestCase):
    def _native(self, control, selected):
        return NonCallableMock(
            spec_set=[
                "root",
                "control_root",
                "manifest_path",
                "manifest_sha256",
                "project_prefix",
            ],
            root=control.parent,
            control_root=control,
            manifest_path=selected.manifest_path,
            manifest_sha256=selected.manifest_sha256,
            project_prefix="AN",
        )

    def test_failed_alias_and_off_path_issue_match_offline_admission(self):
        control, selected = self._standalone_project()
        native = self._native(control, selected)
        alias = control / "_SPEC/AN-S-3039-SPEC-OTHER--engine.md"
        alias.write_text(LEGACY_COMPONENT)
        off_path = (
            control / "_QA/AN-S-3333-SPEC-COMPONENT_MANIFEST--invalid.md"
        )
        off_path.parent.mkdir()
        off_path.write_text("---\ninvalid: [\n---\n")
        self.assertIn(
            "C14", compile_structure(selected, Model())["components"]
        )
        capture = capture_native(native)
        self.assertEqual(
            (),
            model_inputs(native, capture, include_spec_rows=True)[
                "structure_issues"
            ],
        )
        alias.write_text(LEGACY_COMPONENT.replace("version: 4", "version: 0"))
        with self.assertRaisesRegex(ValueError, "Native State"):
            compile_structure(selected, Model())
        capture = capture_native(native)
        inputs = model_inputs(native, capture, include_spec_rows=True)
        issues = inputs["structure_alias_issues"]
        self.assertEqual(
            [alias.relative_to(native.root).as_posix()],
            [issue["relative_path"] for issue in issues],
        )
        with self.assertRaises(StructureAdmissionError):
            compile_structure_rows(
                native.root,
                "control",
                native.manifest_sha256,
                Model(),
                inputs["spec_rows"],
                manifest_path=selected.manifest_path.name,
                alias_issues=issues,
            )

    def test_failed_custom_alias_is_classified_by_admitted_model(self):
        control, selected = self._standalone_project()
        native = self._native(control, selected)
        alias = control / "_SPEC/AN-S-3039-SPEC-OTHER--engine.md"
        alias.write_text(
            LEGACY_COMPONENT.replace(
                "template: component_manifest", "template: new_component"
            ).replace("version: 4", "version: 0")
        )

        class ConfiguredModel(Model):
            def fixed_property_value(self, name, property_name):
                return "new_component"

        self.assertEqual(
            {}, compile_structure(selected, Model())["components"]
        )
        with self.assertRaisesRegex(ValueError, "Native State"):
            compile_structure(selected, ConfiguredModel())
        inputs = model_inputs(
            native, capture_native(native), include_spec_rows=True
        )
        args = (native.root, "control", native.manifest_sha256)
        kwargs = {
            "manifest_path": selected.manifest_path.name,
            "alias_issues": inputs["structure_alias_issues"],
        }
        self.assertEqual(
            {},
            compile_structure_rows(
                *args, Model(), inputs["spec_rows"], **kwargs
            )["components"],
        )
        with self.assertRaises(StructureAdmissionError):
            compile_structure_rows(
                *args, ConfiguredModel(), inputs["spec_rows"], **kwargs
            )

    def test_component_carrier_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            shutil.copyfile(PROJECT, control / PROJECT.name)
            (control / COMPONENT.name).symlink_to(COMPONENT)
            with self.assertRaises(OSError):
                compile_structure(selection(control), Model())

    def test_legacy_component_manifest_requires_tier_four(self):
        control, selected = self._standalone_project()
        path = control / "_SPEC" / COMPONENT.name
        raw = LEGACY_COMPONENT
        _, frontmatter, body = raw.split("---", 2)
        header = yaml.safe_load(frontmatter)
        header["tier"] = 4
        path.write_text(f"---\n{yaml.safe_dump(header)}---{body}")
        fields = compile_structure(selected, Model())["components"]["C14"][
            "fields"
        ]
        self.assertEqual(fields["tier"], 4)
        header["tier"] = 1
        path.write_text(f"---\n{yaml.safe_dump(header)}---{body}")
        with self.assertRaisesRegex(ValueError, "Tier 1 Component Manifest"):
            compile_structure(selected, Model())
        header["tier"] = 0
        path.write_text(f"---\n{yaml.safe_dump(header)}---{body}")
        with self.assertRaisesRegex(ValueError, "identity or parent"):
            compile_structure(selected, Model())

    def test_canonical_tier_one_component_is_discovered_in_project_layout(
        self,
    ):
        control, selected = self._standalone_project()
        project = selected.manifest_path
        project.write_text(
            project.read_text().replace(
                "01_TIER_1_ARCHITECTURE", "01_CUSTOM_ARCHITECTURE", 1
            )
        )
        directory = control / "01_CUSTOM_ARCHITECTURE"
        directory.mkdir()
        path = directory / COMPONENT.name
        _, frontmatter, _ = COMPONENT.read_text().split("---", 2)
        header = yaml.safe_load(frontmatter)
        header["tier"] = 1
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n" + CANONICAL_BODY)
        result = compile_structure(selection(control, project), Model())
        self.assertEqual(result["components"]["C14"]["fields"]["tier"], 1)
        self.assertEqual(
            result["components"]["C14"]["source_path"],
            f"01_CUSTOM_ARCHITECTURE/{COMPONENT.name}",
        )
        _, purpose = project.read_text().split("## Purpose\n", 1)
        root_purpose = purpose.split("\n## ", 1)[0].strip()
        self.assertEqual(root_purpose, result["project"]["purpose"])
        self.assertEqual(
            "Provide the engine.", result["components"]["C14"]["purpose"]
        )

        selected = selection(control, project)
        native = self._native(control, selected)
        rows = model_inputs(
            native, capture_native(native), include_spec_rows=True
        )["spec_rows"]
        self.assertEqual(
            result,
            compile_structure_rows(
                control.parent,
                control.name,
                selected.manifest_sha256,
                Model(),
                rows,
            ),
        )

    def _lens_groups(self, project):
        groups = {
            "SWE": ["SWD", "QA", "DevOps"],
            "SYS": ["SWE", "DOM"],
            "BACKEND": ["API", "SWE"],
            "OTHER": ["SWD2", "API"],
        }
        project.write_text(
            PROJECT.read_text().replace(
                "parameters={",
                "parameters={\n        "
                f"'project': {{'lens_groups': {groups!r}}},",
                1,
            )
        )
        return groups

    def test_component_lens_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            control = Path(tmp).resolve()
            project = control / PROJECT.name
            child = control / COMPONENT.name
            second = control / "AN-S-4000-SPEC-COMPONENT_MANIFEST--second.md"
            groups = self._lens_groups(project)
            original = LEGACY_COMPONENT
            old_lenses = (
                "lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD']"
            )

            def write_component(path, lenses, content=original):
                path.write_text(
                    content.replace(old_lenses, f"lens_whitelist={lenses!r}")
                )

            write_component(child, ["SWE", "SWD", "SWD/DBT"])
            compile_structure(selection(control), Model())
            write_component(child, ["SYS", "BACKEND"])
            with self.assertRaises(ValueError) as raised:
                compile_structure(selection(control), Model())
            for value in (child.name, "SYS", "BACKEND"):
                self.assertIn(value, str(raised.exception))

            write_component(child, ["SYS"])
            write_component(
                second,
                ["BACKEND"],
                original.replace("AN-S-3039", "AN-S-4000").replace(
                    "C14", "C15"
                ),
            )
            compile_structure(selection(control), Model())
            second.unlink()
            write_component(child, ["SWE", "OTHER"])
            compile_structure(selection(control), Model())

            project.write_text(
                project.read_text().replace(
                    repr(groups),
                    repr({"SYS": ["BACKEND"], "BACKEND": ["SYS"]}),
                )
            )
            with self.assertRaisesRegex(ValueError, "(?i)cycle"):
                compile_structure(selection(control), Model())

    def test_formal_fields(self):
        claim = (
            "## Claim\n\n### Formal Claim\n\n```python\nfrom "
            "anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import ComponentManifest\n"
            'declare_entity(entity_name="Component '
            'Manifest", '
            'instance=ComponentManifest(component_id="C1",'
            ' name="One", lens_whitelist=["SPEC"]))\n```\n'
        )
        control, selected = self._standalone_project()
        _, frontmatter, _ = COMPONENT.read_text().split("---", 2)
        header = yaml.safe_load(frontmatter)
        header["tier"] = 4
        path = control / "_SPEC" / COMPONENT.name
        path.write_text(f"---\n{yaml.safe_dump(header)}---\n{claim}")
        fields = compile_structure(selected, Model())["components"]["C1"][
            "fields"
        ]
        self.assertEqual(
            {
                key: fields[key]
                for key in ("component_id", "name", "lens_whitelist")
            },
            {"component_id": "C1", "name": "One", "lens_whitelist": ["SPEC"]},
        )
