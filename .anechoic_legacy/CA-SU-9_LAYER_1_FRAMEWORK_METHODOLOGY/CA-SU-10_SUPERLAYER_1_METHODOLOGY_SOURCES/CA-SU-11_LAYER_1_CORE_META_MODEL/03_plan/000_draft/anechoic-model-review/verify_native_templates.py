"""Run the candidate Spec templates and one local extension through the shared Model."""

import json
from pathlib import Path
import sys
from types import ModuleType
import unittest


PROGRAMMATIC = Path.cwd() / "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC"
sys.path[:0] = [str(PROGRAMMATIC), str(PROGRAMMATIC / "FEATURE_TOOLS")]

from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_classes
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
    _check_relation_references, _relation_registry,
)
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.reviewed_instance_check import bind_reviewed_instance_check
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.validate_model_instance import validate_model_instance
from verify_native_graph import ATOM_CLAIM_SHA256


REVIEWED = {
    "check_atom_identity": ATOM_CLAIM_SHA256,
    "check_project_manifest": "b68c693a62ef4e85fa2183582ffbc9b27d7e5391e7ca5c604e7be3a8d14d5c78",
    "check_component_manifest": "47532369ca1bc4cbd73611f09a27b6142aafb453e1eb156b10198bc4d98dc978",
    "check_purpose": "a080c8a08f9b2f066992045de8183f532eb0aa6fb1dc566e746bc3bed2701a3b",
    "check_component_purpose": "0e2405b84739f53ad22f70f2db415ab7576996b295592d2c63863abaab7a0e13",
    "check_contract": "087afdc97f4a8add78336871fbf1f3698718b97200fad1518f96ef8c20a72007",
    "check_package_spec": "8fb0a7cb026469fd2d3a020be0f9eb852dd4fc16b4c4610fa4131f39b24e698b",
}


def model_validator(records, module_name, add_cleanup):
    _check_relation_references(records)
    module = ModuleType(module_name)
    sys.modules[module_name] = module
    add_cleanup(sys.modules.pop, module_name)
    exec(assemble_model_classes(claim for _, _, claim in records), vars(module))

    parsed = [(source, subject, parse_native_model_claim(claim)) for source, subject, claim in records]
    constraints, types, population = bind_model_declarations(
        [(subject, claim) for _, subject, claim in parsed], vars(module),
    )
    endpoints = _relation_registry(parsed)
    checks = {}
    for (_, subject, claim), (_, _, declaration) in zip(records, parsed, strict=True):
        if check := declaration.get("instance_check"):
            name = check["name"]
            checks[check["parameter_type"]] = (name, bind_reviewed_instance_check(
                claim, reference=subject, reviewed_claim_sha256=REVIEWED[name], model_types=vars(module),
            ))

    def validate(entity_name, outgoing_relations=None, *, peers=(), **properties):
        model_class = types[entity_name]
        return validate_model_instance(
            model_class, properties=properties, outgoing_relations=outgoing_relations or {},
            relation_declarations=constraints, model_types=types, endpoint_registry=endpoints,
            checks=dict(checks[base.__name__] for base in model_class.__mro__ if base.__name__ in checks),
            population_declarations=population, population_peers={types["Atom"]: peers},
        )

    return types, validate


class NativeTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = [
            (name, row["subject"], row["claim"])
            for name in ("native-graph-claims.json", "native-spec-template-claims.json")
            for row in json.loads(Path(__file__).with_name(name).read_text())
        ]
        cls.types, validate = model_validator(cls.records, "_anechoic_template_review", cls.addClassCleanup)
        cls.validate = staticmethod(validate)
        cls.project = validate("Project")
        cls.owner = validate("Component", {"CHILD_OF": [cls.project]})

    def atom(self, entity, owner, atom_id="AN-S-123", version=1, *, peers=(), **content):
        return self.validate(
            entity, {"CONTAINED_BY": [owner]}, atom_id=atom_id, ref_id=f"{atom_id}@{version}",
            version=version, peers=peers, **content,
        )

    def test_generated_asset_matches_claims(self):
        expected = Path(__file__).with_name("anechoic_model.py").read_bytes()
        for records in (self.records, reversed(self.records)):
            generated = assemble_model_classes(claim for _, _, claim in records)
            self.assertEqual(generated.encode("utf-8"), expected)

    def test_project_manifest_and_goal(self):
        identity = {"name": "Anechoic", "prefix": "AN"}
        parameters = {f"option{i}": i for i in range(18)}
        manifest = self.atom("Project Manifest", self.project, tier=-1,
                             parameters=parameters, **identity)
        goal = self.atom("Project Goal", self.project, tier=-1, purpose="Host the review model.")
        self.assertEqual(manifest.control_flow, "Declarative")
        self.assertIsInstance(goal, self.types["Purpose"])
        self.assertIsInstance(goal, self.types["Spec Atom"])
        self.assertIsInstance(manifest, self.types["Spec Atom"])
        self.assertEqual((manifest.name, manifest.prefix), ("Anechoic", "AN"))
        self.assertIsNone(manifest.lens_whitelist)
        explicit = self.atom("Project Manifest", self.project, tier=-1,
                             lens_whitelist=["SPEC"], **identity)
        self.assertEqual(explicit.lens_whitelist, ["SPEC"])
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            self.atom("Project Manifest", self.project, tier=-1,
                      parameters=parameters | {"extra": False}, **identity)
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            self.atom("Project Manifest", self.project, tier=-1,
                      parameters=parameters, lens_whitelist=["SPEC"], **identity)
        with self.assertRaisesRegex(ValueError, "check_project_manifest"):
            self.atom("Project Manifest", self.project, tier=-1, name="", prefix="AN")
        for kind, content in (("Project Manifest", identity), ("Project Goal", {"purpose": "Build."})):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(ValueError, "tier: value must be one of -1"):
                    self.atom(kind, self.project, tier=0, **content)
                with self.assertRaisesRegex(ValueError, "CONTAINED_BY: invalid target kind"):
                    self.atom(kind, self.owner, tier=-1, **content)
        with self.assertRaisesRegex(ValueError, "check_purpose"):
            self.atom("Project Goal", self.project, tier=-1, purpose=" ")

    def test_child_manifest_and_purpose(self):
        properties = {"component_id": "C43", "name": "Backend Deck"}
        manifest = self.atom("Component Manifest", self.owner, tier=0, layer=2, **properties)
        self.assertEqual(manifest.component_id, "C43")
        self.assertIsNone(self.atom("Component Manifest", self.owner, tier=0, **properties).layer)
        self.atom("Component Manifest", self.project, tier=0, **properties)
        purpose = self.atom("Component Purpose", self.owner, tier=0, component_id="C43", purpose="Read and write.")
        self.assertIsInstance(purpose, self.types["Purpose"])
        for kind, content in (("Component Manifest", properties),
                              ("Component Purpose", {"component_id": "C43", "purpose": "Serve callers."})):
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "tier: value must be one of 0"):
                self.atom(kind, self.owner, tier=-1, **content)
        with self.assertRaisesRegex(ValueError, "component_id: occurrence count 0"):
            self.atom("Component Manifest", self.owner, tier=0, name="Backend Deck")
        with self.assertRaisesRegex(ValueError, "check_component_purpose"):
            self.atom("Component Purpose", self.owner, tier=0, component_id=" ", purpose="Serve callers.")
        with self.assertRaisesRegex(ValueError, "CONTAINED_BY: invalid target kind"):
            self.atom("Component Manifest", self.validate("Package"), tier=0, **properties)

    def test_root_contract_and_child_contract(self):
        guarantee = "Queries finish within 500 ms under the stated load."
        self.atom("Contract", self.project, guarantee=guarantee)
        self.atom("Contract", self.project, guarantee=guarantee, tier=2)
        contract = self.atom("Component Contract", self.owner, guarantee=guarantee, tier=1)
        self.assertIsInstance(contract, self.types["Contract"])
        self.assertIsInstance(contract, self.types["Spec Atom"])
        with self.assertRaisesRegex(ValueError, "tier: occurrence count 0"):
            self.atom("Component Contract", self.owner, guarantee=guarantee)
        with self.assertRaisesRegex(ValueError, "tier: value must be one of 1"):
            self.atom("Component Contract", self.owner, guarantee=guarantee, tier=0)
        with self.assertRaisesRegex(ValueError, "check_contract"):
            self.atom("Component Contract", self.owner, guarantee=" ", tier=1)

    def test_package_has_separate_id_purpose_and_contract(self):
        properties = {"package_id": "pkg3344", "purpose": "Create orders.", "contract": "Expose create()."}
        first = self.atom("Package Spec", self.owner, **properties)
        second = self.atom("Package Spec", self.owner, version=2, peers=[first], tier=3, **properties)
        self.assertEqual((first.atom_id, first.package_id), (second.atom_id, second.package_id))
        self.assertNotEqual(first.atom_id, first.package_id)
        self.assertIsInstance(first, self.types["Spec Atom"])
        for missing in properties:
            with self.subTest(missing=missing), self.assertRaisesRegex(ValueError, f"{missing}: occurrence count 0"):
                self.atom("Package Spec", self.owner, **{k: v for k, v in properties.items() if k != missing})
        for invalid in ({"package_id": "AN-S-123"}, {"purpose": " "}, {"contract": " "}):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "check_package_spec"):
                self.atom("Package Spec", self.owner, **(properties | invalid))
        with self.assertRaisesRegex(ValueError, "check_atom_identity"):
            self.atom("Package Spec", self.owner, atom_id="AN-P-123", **properties)

    def test_synthetic_local_pmeta_component_extension(self):
        extension = self.atom("PMETA Atom", self.project, atom_id="LOCAL-P-17")
        claim = """from anechoic.formal_claims import declare_entity
from anechoic.model import Component

class ReviewComponent(Component):
    pass

declare_entity(entity_name="Review Component", entity_class=ReviewComponent)
"""
        extension_record = (
            extension.ref_id, "MODEL//LOCAL <+ Node//Artifact//Component//Review Component", claim,
        )
        local_types, validate_local = model_validator(
            [*self.records, extension_record], "_anechoic_local_template_review", self.addCleanup,
        )
        parent = validate_local("Project")
        local_child = validate_local("Review Component", {"CHILD_OF": [parent]})
        self.assertIsInstance(local_child, local_types["Component"])
        self.assertEqual(local_child.__dataclass_fields__, local_types["Component"].__dataclass_fields__)
        with self.assertRaisesRegex(ValueError, "CHILD_OF: target count 0"):
            validate_local("Review Component")
        self.assertNotIn("Review Component", self.types)
        self.assertEqual(self.project, self.validate("Project"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
