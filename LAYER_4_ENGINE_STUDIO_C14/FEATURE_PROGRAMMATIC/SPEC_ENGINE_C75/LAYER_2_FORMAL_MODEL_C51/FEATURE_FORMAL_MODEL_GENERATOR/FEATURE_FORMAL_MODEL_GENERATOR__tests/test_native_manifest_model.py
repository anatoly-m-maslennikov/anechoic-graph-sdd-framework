import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass, is_pydantic_dataclass

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.native.native_manifest_model import (
    load_native_model,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.native import (
    native_manifest_model,
)


class NativeManifestModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = load_native_model()
        cls.fields = {
            "atom_id": "AN-S-123",
            "ref_id": "AN-S-123@1",
            "version": 1,
            "tier": -1,
            "name": "Anechoic",
            "prefix": "AN",
        }

    def test_reviewed_classes_are_pydantic_dataclasses(self):
        self.assertTrue(
            all(
                is_pydantic_dataclass(cls)
                for cls in self.model._types.values()
            )
        )

    def test_reviewed_manifest_validation(self):
        fields = self.fields | {
            "parameters": {f"option{i}": i for i in range(18)}
        }
        self.assertEqual(
            self.model.validate_manifest(fields, "C00").name, "Anechoic"
        )
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            self.model.validate_manifest(
                fields | {"parameters": fields["parameters"] | {"extra": 1}},
                "C00",
            )
        with self.assertRaisesRegex(ValueError, "check_atom_identity"):
            self.model.validate_manifest(
                fields | {"ref_id": "AN-S-123@2"}, "C00"
            )
        with self.assertRaisesRegex(ValueError, "Project C00"):
            self.model.validate_manifest(fields, "C01")

    def test_project_config_identity_accepts_current_and_legacy_markers(self):
        check = self.model._checks["Atom"][1]
        for marker in ("C", "P"):
            atom_id = f"AN-{marker}-1"
            atom = self.model._types["Project Config Atom"](
                atom_id=atom_id, version=1, ref_id=f"{atom_id}@1"
            )
            self.assertTrue(check(atom))
        atom.atom_id = "AN-S-1"
        atom.ref_id = "AN-S-1@1"
        self.assertFalse(check(atom))

    def test_reviewed_component_manifest_accepts_optional_boundaries(self):
        fields = {
            "atom_id": "AN-S-124",
            "ref_id": "AN-S-124@1",
            "version": 1,
            "tier": 4,
            "component_id": "C01",
            "name": "Engine",
        }
        boundaries = {"code": {"imports": ["C02"]}}
        self.assertIsNone(
            self.model.validate_component_manifest(fields, "C00").boundaries
        )
        manifest = self.model.validate_component_manifest(
            fields | {"boundaries": boundaries}, "C00"
        )
        self.assertEqual(manifest.boundaries, boundaries)
        self.assertEqual(
            self.model.validate_component_manifest(
                fields | {"tier": 1}, "C00"
            ).tier,
            1,
        )
        with self.assertRaises(ValueError):
            self.model.validate_component_manifest(fields | {"tier": 0}, "C00")
        with self.assertRaisesRegex(ValueError, "boundaries:"):
            self.model.validate_component_manifest(
                fields | {"boundaries": ["C02"]}, "C00"
            )

    def test_active_component_manifest_tier_is_used(self):
        records, _, _ = native_manifest_model.reviewed_model_records()
        active = []
        for path, subject, claim in records:
            if subject.endswith("//Component Manifest"):
                claim = claim.replace(
                    'allowed_values": (1, 4)', 'allowed_values": (0,)'
                )
            active.append((path, subject, claim))
        model = native_manifest_model._NativeModel(records=active)
        fields = {
            "atom_id": "AN-S-124",
            "ref_id": "AN-S-124@1",
            "version": 1,
            "tier": 0,
            "component_id": "C01",
            "name": "Engine",
        }
        self.assertEqual(
            model.validate_component_manifest(fields, "C00").tier, 0
        )
        with self.assertRaises(ValueError):
            model.validate_component_manifest(fields | {"tier": 4}, "C00")

    def test_component_seed_checks_identity_and_optional_prose(
        self,
    ):
        fields = {
            "atom_id": "AN-S-125",
            "ref_id": "AN-S-125@1",
            "version": 1,
            "tier": 2,
            "component_seed_id": "CS123",
        }
        seed = self.model.validate_component_seed_manifest(fields, "C01")
        self.assertEqual(
            (seed.purpose, seed.contract, seed.solution), (None, None, None)
        )
        prose = {
            "purpose": "Purpose",
            "contract": "Contract",
            "solution": "Solution",
        }
        seed = self.model.validate_component_seed_manifest(
            fields | prose, "C01"
        )
        self.assertEqual(
            (seed.purpose, seed.contract, seed.solution), tuple(prose.values())
        )
        for seed_id in ("CS", "CS１２", "pkg1", "CS1x"):
            with (
                self.subTest(seed_id=seed_id),
                self.assertRaisesRegex(
                    ValueError, "check_component_seed_manifest"
                ),
            ):
                self.model.validate_component_seed_manifest(
                    fields | {"component_seed_id": seed_id}, "C01"
                )

    def test_release_workflow_setting_is_an_optional_exact_boolean(self):
        self.model.validate_manifest(
            self.fields | {"parameters": {"project_mcp": {}}}, "C00"
        )
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                parameters = {
                    "project_mcp": {"release_workflows_enabled": enabled}
                }
                manifest = self.model.validate_manifest(
                    self.fields | {"parameters": parameters}, "C00"
                )
                self.assertIs(
                    manifest.parameters["project_mcp"][
                        "release_workflows_enabled"
                    ],
                    enabled,
                )
        for invalid in (1, "true", None):
            with self.subTest(invalid=invalid):
                parameters = {
                    "project_mcp": {"release_workflows_enabled": invalid}
                }
                with self.assertRaisesRegex(
                    ValueError, "check_project_manifest"
                ):
                    self.model.validate_manifest(
                        self.fields | {"parameters": parameters}, "C00"
                    )

    def test_derived_ref_id_input_is_checked_and_not_passed_to_constructor(
        self,
    ):
        @dataclass(config=ConfigDict(strict=True, extra="forbid"))
        class StrictAtom:
            atom_id: str
            version: int

            @property
            def ref_id(self):
                return f"{self.atom_id}@{self.version}"

        def validate(cls, *, properties, **kwargs):
            return cls(**properties)

        with (
            patch.dict(self.model._types, {"Strict": StrictAtom}),
            patch.object(
                native_manifest_model,
                "validate_model_instance",
                side_effect=validate,
            ),
        ):
            fields = {
                "atom_id": "AN-S-123",
                "version": 1,
                "ref_id": "AN-S-123@1",
            }
            self.assertEqual(
                self.model._validate("Strict", fields, {}).ref_id,
                fields["ref_id"],
            )
            self.assertIn("ref_id", fields)
            with self.assertRaisesRegex(ValueError, "differs from derived"):
                self.model._validate(
                    "Strict", fields | {"ref_id": "AN-S-123@2"}, {}
                )

    def test_containment_is_checked_by_the_reviewed_model(self):
        project = self.model._validate("Project", {}, {})
        component = self.model._validate(
            "Component", {}, {"CHILD_OF": [project]}
        )
        with self.assertRaisesRegex(
            ValueError, "CONTAINED_BY: invalid target kind"
        ):
            self.model._validate(
                "Project Manifest", self.fields, {"CONTAINED_BY": [component]}
            )

    def test_claim_file_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "native-graph-claims.json"
            path.write_bytes(b"[]")
            with patch.object(
                native_manifest_model, "_ASSETS", Path(directory)
            ):
                with self.assertRaisesRegex(
                    ValueError, "reviewed Claim file differs"
                ):
                    native_manifest_model._NativeModel()


if __name__ == "__main__":
    unittest.main()
