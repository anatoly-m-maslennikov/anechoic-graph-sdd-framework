import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.\
    _package__shared import (load_boundary_model, load_manifest)  # fmt: skip

from .test_boundary_model import _inputs


class EmbeddedContractTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.manifest, self.contract, self.solution = _inputs(self.root)
        self.manifest.update(status="draft", container_component="C10")
        self.manifest_path = self.root / self.manifest["path"]
        self.solution_path = self.root / self.solution["path"]
        self.legacy_manifest_source = (
            self.manifest_path.read_text()
            .replace("tier: 4", "tier: 1")
            .replace("status: active", "status: draft")
            .replace("component: C7", "component: C10")
        )
        self.manifest_path.write_text(
            self.legacy_manifest_source.partition("## Formal Manifest")[0]
            + (
                "\n## Summary\n\nDeclare the Test Component.\n\n## Purpo"
                "se\n\nTest the boundary model.\n\n## Component Identit"
                "y\n\n```python\nfrom anechoic.formal_claims import de"
                "clare_entity\nfrom anechoic.model import ComponentM"
                "anifest\ndeclare_entity(entity_name='Component Mani"
                "fest', instance=ComponentManifest(component_id='C7"
                "', name='Test'))\n```\n\n## Component Boundaries\n\n```"
                "python\n{'io': {'server': 'API'}}\n```\n\n## Component"
                " Contract\n\n```python contract\ndeclare_contract()\n`"
                "``\n"
            )
        )
        self.solution_path.write_text(
            self.solution_path.read_text()
            .replace("tier: 1", "tier: 0")
            .replace("template: decision", "template: solution")
            .replace(
                "IS_SOLUTION_FOR: [AN-S-2@1]", "ANSWERS: [AN-S-1@1-draft]"
            )
        )

    def load(self):
        return load_boundary_model(
            self.root, "C7", self.manifest, solution=self.solution
        )

    def test_model_uses_one_manifest_pin_for_both_declarations(self):
        (self.root / self.contract["path"]).unlink()
        model = self.load()
        self.assertTrue(model["embedded_contract"])
        self.assertEqual([], model["issues"])
        self.assertEqual(
            model["manifest"]["source"], model["contract"]["source"]
        )
        self.assertEqual(
            "C10", model["contract"]["source"]["container_component"]
        )
        self.assertEqual(
            [("python contract", "declare_contract()\n")],
            model["contract"]["claims"],
        )
        self.assertEqual(
            model,
            load_boundary_model(self.root, "C7", self.manifest, self.solution),
        )
        with self.assertRaisesRegex(
            ValueError, "Contract source is the pinned Manifest"
        ):
            load_boundary_model(
                self.root, "C7", self.manifest, self.contract, self.solution
            )
        self.solution_path.unlink()
        self.assertEqual(
            model["contract"],
            load_manifest(self.root, "C7", self.manifest)["contract"],
        )

    def test_solution_must_answer_the_exact_manifest_revision(self):
        source = self.solution_path.read_text()
        for relation in (
            "ANSWERS: [AN-S-1]",
            "ANSWERS: [AN-S-1@1]",
            "ANSWERS: [AN-S-1@2-draft]",
            "IS_SOLUTION_FOR: [AN-S-1@1-draft]",
        ):
            with self.subTest(relation=relation):
                self.solution_path.write_text(
                    source.replace("ANSWERS: [AN-S-1@1-draft]", relation)
                )
                with self.assertRaisesRegex(
                    ValueError, "missing exact ANSWERS link to AN-S-1@1-draft"
                ):
                    self.load()

    def test_solution_must_have_tier_zero_and_belong_to_the_component(self):
        source = self.solution_path.read_text()
        self.solution_path.write_text(source.replace("tier: 0", "tier: 1"))
        with self.assertRaisesRegex(ValueError, "solution must have Tier 0"):
            self.load()
        self.solution_path.write_text(
            source.replace("component: C7", "component: C10")
        )
        self.solution["container_component"] = "C10"
        with self.assertRaisesRegex(
            ValueError, "solution component does not match"
        ):
            self.load()

    def test_only_tier_one_admits_the_embedded_contract(self):
        source = self.manifest_path.read_text()
        self.manifest_path.write_text(source.replace("tier: 1", "tier: 4"))
        with self.assertRaises(ValueError):
            load_manifest(self.root, "C7", self.manifest)

    def \
   test_identity_only_manifest_loads_and_verification_reports_missing_contract(
            self,
        ):  # fmt: skip
        source = self.manifest_path.read_text()
        header = source.partition("## Summary")[0]
        identity = source[
            source.index("## Component Identity") : source.index(
                "## Component Boundaries"
            )
        ]
        self.manifest_path.write_text(header + identity)
        manifest = load_manifest(self.root, "C7", self.manifest)
        self.assertEqual(manifest["fields"]["component_id"], "C7")
        self.assertNotIn("contract", manifest)
        self.assertIsNone(manifest["boundaries"])
        with self.assertRaisesRegex(ValueError, "missing Contract claim"):
            self.load()

    def test_verification_reports_missing_solution_source(self):
        with self.assertRaisesRegex(ValueError, "missing Solution source"):
            load_boundary_model(self.root, "C7", self.manifest)
