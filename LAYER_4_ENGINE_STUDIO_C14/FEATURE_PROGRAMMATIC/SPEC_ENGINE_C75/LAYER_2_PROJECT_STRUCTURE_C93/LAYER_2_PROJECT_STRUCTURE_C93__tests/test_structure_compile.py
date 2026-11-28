import json
import unittest
from unittest.mock import NonCallableMock, patch

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.carriers.content.content__shared import (
    CarrierError,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import (
    LimitReached,
    ReadContext,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.structure.structure__shared import (
    read_structure,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.carriers.content.carrier_read__pub import (
    parse_carrier,
)
from ....FEATURE_TOOLS.ADAPTERS_C30.settings.project.project_manifest__pub import (
    manifest_summary_fields,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.\
    PROJECT_SUPPORT.PROJECT_SELECTION.\
    PROJECT_SELECTION__shared import (
    resolve_native_project,
)
from ..LAYER_2_PROJECT_STRUCTURE_C93__shared import (
    _validation_fields,
    compile_structure,
)
from .structure_fixtures import (
    COMPONENT,
    CONTROL,
    LEGACY_COMPONENT,
    ROOT,
    Model,
    PROJECT,
    StructureFixture,
)


class StructureTests(StructureFixture, unittest.TestCase):
    def test_project_summary_follows_model_declaration(self):
        model = Model()
        summaries = []

        def validate(fields, parent):
            summaries.append(fields.get("summary"))
            model.validate_manifest(fields, parent)
            manifest = NonCallableMock(
                spec_set=["name", "prefix"],
                prefix=fields["prefix"],
            )
            manifest.name = fields["name"]
            return manifest

        resolve_native_project(
            ROOT,
            CONTROL.name,
            validate_manifest=validate,
            require_manifest_summary=True,
        )
        resolve_native_project(ROOT, CONTROL.name, validate_manifest=validate)
        carrier = parse_carrier(PROJECT.read_bytes(), PROJECT)
        expected = manifest_summary_fields(carrier)["summary"]
        self.assertEqual([expected, None], summaries)
        self.assertEqual(
            {},
            manifest_summary_fields(
                NonCallableMock(spec_set=["body"], body="## Claim\n\nText\n")
            ),
        )
        with self.assertRaisesRegex(ValueError, "duplicate Summary"):
            manifest_summary_fields(
                NonCallableMock(
                    spec_set=["body"],
                    body="## Summary\n\nOne\n\n## Summary\n\nTwo\n",
                )
            )

    def test_component_and_seed_summary_follows_model_declaration(self):
        carrier = NonCallableMock(
            spec_set=["body", "metadata"],
            body="## Summary\n\nAuthored summary.\n",
            metadata={},
        )
        model = NonCallableMock(
            spec_set=["requires_atom_state", "declares_summary"],
            requires_atom_state=False,
            declares_summary=lambda name: name == "Component Manifest",
        )
        self.assertEqual(
            {"summary": "Authored summary."},
            _validation_fields({}, carrier, model, "Component Manifest"),
        )
        self.assertEqual(
            {},
            _validation_fields({}, carrier, model, "Component Seed Manifest"),
        )
        self.assertEqual(
            {}, _validation_fields({}, carrier, Model(), "Component Manifest")
        )
        model.declares_summary = lambda _: True
        seed = NonCallableMock(
            spec_set=["body", "metadata"],
            body="# Manifest Build\n\n## Purpose\n\nBuild.\n",
            metadata={},
        )
        self.assertEqual(
            {"summary": "Manifest Build"},
            _validation_fields({}, seed, model, "Component Seed Manifest"),
        )
        for body in ("## Purpose\n\nBuild.\n", "# One\n\n# Two\n"):
            with self.assertRaisesRegex(ValueError, "requires one title"):
                _validation_fields(
                    {},
                    NonCallableMock(
                        spec_set=["body", "metadata"], body=body, metadata={}
                    ),
                    model,
                    "Component Seed Manifest",
                )

    def test_component_template_comes_from_header_when_model_declares_it(self):
        carrier = parse_carrier(LEGACY_COMPONENT.encode(), COMPONENT)
        model = NonCallableMock(
            spec_set=["requires_atom_state", "declares_property"],
            requires_atom_state=False,
            declares_property=lambda name, prop: (
                name == "Component Manifest" and prop == "template"
            ),
        )
        self.assertEqual(
            {"template": "component_manifest"},
            _validation_fields({}, carrier, model, "Component Manifest"),
        )
        changed = NonCallableMock(
            spec_set=["body", "metadata"],
            body=carrier.body,
            metadata={
                **carrier.metadata,
                "context": {
                    **carrier.metadata["context"],
                    "template": "other",
                },
            },
        )
        self.assertEqual(
            {"template": "other"},
            _validation_fields({}, changed, model, "Component Manifest"),
        )
        self.assertEqual(
            {}, _validation_fields({}, changed, Model(), "Component Manifest")
        )
        self.assertEqual(
            {},
            _validation_fields({}, changed, model, "Component Seed Manifest"),
        )

    def test_offline_compile_validates_project_manifest_with_supplied_model(
        self,
    ):
        _, selected = self._standalone_project()
        model = Model()
        with (
            patch.object(
                model,
                "validate_manifest",
                side_effect=ValueError("Project refused"),
            ),
            self.assertRaisesRegex(ValueError, "Project refused"),
        ):
            compile_structure(selected, model)

    def test_component_scanner_uses_model_template(self):
        control, selected = self._standalone_project()
        component = control / "_SPEC" / COMPONENT.name
        component.write_text(
            LEGACY_COMPONENT.replace(
                "template: component_manifest", "template: new_component"
            )
        )

        class ConfiguredModel(Model):
            def fixed_property_value(self, name, property_name):
                assert (name, property_name) == (
                    "Component Manifest",
                    "template",
                )
                return "new_component"

            def declares_property(self, name, property_name):
                return (name, property_name) == (
                    "Component Manifest",
                    "template",
                )

            def validate_component_manifest(self, fields, parent_id):
                super().validate_component_manifest(fields, parent_id)
                assert fields["template"] == "new_component"

        self.assertIn(
            "C14", compile_structure(selected, ConfiguredModel())["components"]
        )
        component.write_text(LEGACY_COMPONENT)
        self.assertNotIn(
            "C14", compile_structure(selected, ConfiguredModel())["components"]
        )
        self.assertIn(
            "C14", compile_structure(selected, Model())["components"]
        )

    def test_seed_optional_sections_survive_structure_compilation(self):
        control, selected = self._standalone_project()
        path = (
            control
            / "_SPEC"
            / "AN-S-4000-SPEC-COMPONENT_SEED_MANIFEST--test.md"
        )
        path.write_text(
            """---
atom_family: SPEC
atom_id: AN-S-4000
container: {component: C00}
tier: 2
context: {template: component_seed_manifest, lens: SPEC}
state: {status: active, version: 1, updated_at: '2026-11-20T00:00:00Z'}
---
# Seed

## Formal Manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentSeedManifest
"""
            + 'declare_entity(entity_name="Component Seed Manifest", '
            + 'instance=ComponentSeedManifest(component_seed_id="CS4000", '
            + 'boundaries={"process": {"launch": "worker"}}))'
            + """
```

## Contract

Contract text.
"""
        )
        snapshot = compile_structure(selected, Model())
        snapshot_path = control.parent / "structure.json"
        snapshot_path.write_text(json.dumps(snapshot))
        fields = read_structure(snapshot_path).packages["CS4000"].fields
        self.assertEqual(fields["contract"], "Contract text.")
        self.assertNotIn("purpose", fields)
        self.assertNotIn("solution", fields)
        self.assertEqual(
            dict(fields["boundaries"]["process"]), {"launch": "worker"}
        )

    def test_ordinary_specs_may_be_malformed_unreadable_or_oversized(self):
        control, selected = self._standalone_project()
        spec = control / "_SPEC"
        child = spec / COMPONENT.name
        child.write_text(LEGACY_COMPONENT)
        (control / "AN-S-4000-SPEC-REQUIREMENT--bad.md").write_text(
            "---\ninvalid: [\n---\n"
        )
        (spec / "AN-S-4001-SPEC-REQUIREMENT--unreadable.md").symlink_to(
            spec / "missing.md"
        )
        oversized = spec / "AN-S-4002-SPEC-REQUIREMENT--oversized.md"
        oversized.touch()
        read = ReadContext.read

        def limited(reader, path, **options):
            if path == oversized:
                raise LimitReached("max_file_bytes")
            return read(reader, path, **options)

        with patch.object(ReadContext, "read", limited):
            result = compile_structure(selected, Model())
        self.assertEqual(
            f"_SPEC/{COMPONENT.name}",
            result["components"]["C14"]["source_path"],
        )

    def test_conventional_manifests_require_valid_headers(self):
        control, selected = self._standalone_project()
        for filename in (
            COMPONENT.name,
            "AN-S-4000-SPEC-COMPONENT_SEED_MANIFEST--required.md",
        ):
            with self.subTest(filename=filename):
                path = control / "_SPEC" / filename
                path.write_text("---\ninvalid: [\n---\n")
                with self.assertRaises(CarrierError):
                    compile_structure(selected, Model())
                path.unlink()
