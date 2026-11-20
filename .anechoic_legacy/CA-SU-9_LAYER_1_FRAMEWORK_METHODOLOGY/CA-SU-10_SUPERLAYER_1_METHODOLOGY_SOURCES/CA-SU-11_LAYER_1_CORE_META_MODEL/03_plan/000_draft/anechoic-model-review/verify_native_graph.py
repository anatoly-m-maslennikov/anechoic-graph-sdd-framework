"""Verify the isolated Anechoic graph Claims with the existing Model validators."""

import json
from pathlib import Path
import sys
from types import ModuleType
import unittest


programmatic = Path.cwd() / "LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC"
sys.path[:0] = [str(programmatic), str(programmatic / "FEATURE_TOOLS"), str(programmatic / "FEATURE_APPS")]

from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.relation_registry import RelationRegistry
from APP_WORKBENCH.FEATURE_WORKBENCH_BACKEND.relations import _outgoing_facts
from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_classes
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import (
    _check_relation_references, _relation_registry,
)
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_relation_endpoints import validate_relation_endpoint_levels
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.reviewed_instance_check import bind_reviewed_instance_check
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.validate_model_instance import validate_model_instance


ATOM_CLAIM_SHA256 = "1756b0e117c6b68ae719f52cb805a69d2a2d198feb9a2996b94869698e13cd09"


class NativeGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).with_name("native-graph-claims.json")
        rows = json.loads(path.read_text())
        _check_relation_references([(path.name, row["subject"], row["claim"]) for row in rows])
        model = ModuleType("_anechoic_graph_review")
        sys.modules[model.__name__] = model
        cls.addClassCleanup(sys.modules.pop, model.__name__)
        exec(assemble_model_classes(row["claim"] for row in rows), vars(model))

        declarations = [(row["subject"], parse_native_model_claim(row["claim"])) for row in rows]
        cls.bindings, cls.types, cls.population = bind_model_declarations(declarations, vars(model))
        cls.endpoints = _relation_registry([(path.name, subject, claim) for subject, claim in declarations])
        cls.classification_facts = next(row['facts'] for row in rows
                                       if row['subject'].endswith('Relation//IS_CLASSIFIED_BY'))
        reviewed_atom_claim = next(row for row in rows if row["subject"].endswith("//Atom"))
        cls.atom_check = staticmethod(bind_reviewed_instance_check(
            reviewed_atom_claim["claim"], reference=reviewed_atom_claim["subject"],
            reviewed_claim_sha256=ATOM_CLAIM_SHA256,
            model_types=vars(model),
        ))

    def validate(self, name, relations=None, *, peers=(), **properties):
        atom = self.types["Atom"]
        model_class = self.types[name]
        checks = {"check_atom_identity": self.atom_check} if issubclass(model_class, atom) else {}
        return validate_model_instance(
            model_class, properties=properties, outgoing_relations=relations or {},
            relation_declarations=self.bindings, model_types=self.types, checks=checks,
            population_declarations=self.population, population_peers={atom: peers},
            endpoint_registry=self.endpoints,
        )

    def endpoint(self, name, source, target, *, levels=("model_entities", "model_entities")):
        arguments, _ = self.endpoints[name]
        validate_relation_endpoint_levels(
            {"kind": "relation", "arguments": arguments}, name, *levels,
            source_kind=self.types[source], target_kind=self.types[target], model_types=self.types,
        )

    def test_graph_narrowing_and_composition(self):
        for child, base in (
            ("Artifact", "Node"), ("Ephemeral", "Node"), ("Atom", "Artifact"),
            ("Spec Atom", "Atom"), ("Ticket Atom", "Atom"), ("PMETA Atom", "Atom"),
            ("Event Record", "Artifact"), ("Component", "Artifact"), ("Project", "Component"),
            ("Package", "Artifact"), ("Component Package", "Package"),
        ):
            self.assertEqual((self.types[base],), self.types[child].__bases__)
        self.assertNotIsInstance(self.validate("Ephemeral"), self.types["Artifact"])
        for whole, part in (
            ("Model", "Graph"), ("Model", "eDSL"), ("Model", "Carrier"),
            ("Graph", "Node"), ("Graph", "Relation"), ("eDSL", "Format"), ("eDSL", "Cardinality"),
            ("Component", "Component Spec Section"), ("Component", "Component Package"),
            ("Package", "Package"), ("Package", "Module"), ("Module", "Unit"),
        ):
            self.endpoint("CONTAINS", whole, part)
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds"):
            self.endpoint("CONTAINS", "Module", "Package")
        self.validate("Package", {"CONTAINED_BY": [self.validate("Component Package")]})
        with self.assertRaisesRegex(ValueError, "endpoint levels or kinds"):
            self.validate("Unit", {"CONTAINED_BY": [self.validate("Package")]})

    def test_component_and_atom_direct_containment(self):
        project = self.validate("Project")
        component = self.validate("Component", {"CHILD_OF": [project]})
        self.validate("Component", {"CHILD_OF": [component]})
        for name, parents, violation in (
            ("Component", [], "CHILD_OF: target count 0"),
            ("Component", [project, component], "CHILD_OF: target count 2"),
            ("Component", [self.validate("Package")], "CHILD_OF: invalid target kind"),
            ("Component", [self.types["Project"]], "CHILD_OF: endpoint levels or kinds"),
            ("Project", [component], "CHILD_OF: target count 1"),
        ):
            with self.subTest(name=name, violation=violation), self.assertRaisesRegex(ValueError, violation):
                self.validate(name, {"CHILD_OF": parents})
        epic = self.validate("Ticket Atom", {"CONTAINED_BY": [component]},
                             atom_id="AN-T-10", ref_id="AN-T-10@1", version=1)
        task = {"atom_id": "AN-T-11", "ref_id": "AN-T-11@1", "version": 1}
        self.validate("Ticket Atom", {"CONTAINED_BY": [epic]}, **task)
        for containers, violation in (
            ([], "CONTAINED_BY: target count 0"),
            ([epic, component], "CONTAINED_BY: target count 2"),
            ([self.validate("Event Record")], "CONTAINED_BY: invalid target kind"),
        ):
            with self.subTest(violation=violation), self.assertRaisesRegex(ValueError, violation):
                self.validate("Ticket Atom", {"CONTAINED_BY": containers}, **task)
        with self.assertRaisesRegex(ValueError, "CHILDREN: inverse Relation requires explicit permission"):
            self.validate("Project", {"CHILDREN": [component]})

    def test_direct_inverse_materialization(self):
        inverse = {name: args[other] for name, (args, reverse) in self.endpoints.items()
                   if (other := ("relation_name" if reverse else "inverse_alias")) in args}
        registry = RelationRegistry(frozenset(self.endpoints), inverse, {}, frozenset())
        direct_facts = {
            "B": (("Component", "B", "CHILD_OF", "Component", "A"),),
            "C": (("Component", "C", "CHILD_OF", "Component", "B"),),
            "epic": (("Atom", "AN-T-10", "CONTAINED_BY", "Component", "B"),),
            "task": (("Atom", "AN-T-11", "CONTAINED_BY", "Atom", "AN-T-10"),),
        }
        outgoing = _outgoing_facts([], registry, direct_facts)
        self.assertEqual({("Component", "A", "CHILDREN", "Component", "B", True)},
                         outgoing[("Component", "A")])
        self.assertEqual({("Atom", "AN-T-10", "CONTAINS", "Atom", "AN-T-11", True),
                          ("Atom", "AN-T-10", "CONTAINED_BY", "Component", "B", False)},
                         outgoing[("Atom", "AN-T-10")])

    def test_atom_families_and_revision_references(self):
        links = {"CONTAINED_BY": [self.validate("Project")]}
        for name, marker in (("Spec Atom", "S"), ("Ticket Atom", "T"), ("PMETA Atom", "P")):
            atom_id = f"AN-{marker}-123"
            first = self.validate(name, links, atom_id=atom_id, ref_id=f"{atom_id}@1", version=1)
            self.validate(name, links, peers=[first], atom_id=atom_id, ref_id=f"{atom_id}@2", version=2)
            self.validate(name, links, peers=[first], atom_id=atom_id, ref_id=f"{atom_id}@1-draft", version=1)
            with self.assertRaisesRegex(ValueError, "Population uniqueness violated"):
                self.validate(name, links, peers=[first], atom_id=atom_id, ref_id=f"{atom_id}@1", version=1)
        for atom_id in ("AN-S-096", "AN-S-0"):
            self.validate("Spec Atom", links, atom_id=atom_id, ref_id=f"{atom_id}@1", version=1)
        for atom_id, ref_id, version, violation in (
            ("AN-T-123", "AN-T-123@1", 1, "check_atom_identity"),
            ("AN-S-123-DES", "AN-S-123-DES@1", 1, "check_atom_identity"),
            ("AN-S-", "AN-S-@1", 1, "check_atom_identity"),
            ("AN-S-123", "AN-S-123@2", 1, "check_atom_identity"),
            ("AN-S-123", "AN-S-123@1-archived", 1, "check_atom_identity"),
            ("AN-S-123", "AN-S-123@0", 0, "version: value must be at least 1"),
            ("AN-S-123", "AN-S-123@1", "1", "version: Input should be a valid integer"),
        ):
            with self.subTest(atom_id=atom_id, ref_id=ref_id, version=version):
                with self.assertRaisesRegex(ValueError, violation):
                    self.validate("Spec Atom", links, atom_id=atom_id, ref_id=ref_id, version=version)
        with self.assertRaisesRegex(ValueError, "ref_id: occurrence count 0"):
            self.validate("Spec Atom", links, atom_id="AN-S-123", version=1)

    def test_named_classifications(self):
        for member, classification in (
            ("Spec Atom", "Continuant"), ("PMETA Atom", "Continuant"), ("Ticket Atom", "Occurrent"),
            ("Spec Atom", "SSOT"), ("Event Record", "SSOT"),
        ):
            self.endpoint("IS_CLASSIFIED_BY", member, classification)
            self.endpoint("CLASSIFIES", classification, member)
            self.assertFalse(issubclass(self.types[member], self.types[classification]))
        entity = 'Model Entity'
        direct = []
        for fact in self.classification_facts:
            source, name, target = fact['source'], fact['relation'], fact['target']
            self.endpoint(name, source, target)
            direct.append((entity, source, name, entity, target))
        registry = RelationRegistry(frozenset(self.endpoints),
                                    {'IS_CLASSIFIED_BY': 'CLASSIFIES', 'CLASSIFIES': 'IS_CLASSIFIED_BY'},
                                    {}, frozenset())
        outgoing = _outgoing_facts([], registry, {'classification': direct})
        self.assertEqual(outgoing[(entity, 'Spec Atom')], {
            (entity, 'Spec Atom', 'IS_CLASSIFIED_BY', entity, 'Continuant', False),
            (entity, 'Spec Atom', 'IS_CLASSIFIED_BY', entity, 'SSOT', False),
        })
        self.assertEqual(outgoing[(entity, 'Ticket Atom')], {
            (entity, 'Ticket Atom', 'IS_CLASSIFIED_BY', entity, 'Occurrent', False),
        })
        self.assertEqual(outgoing[(entity, 'Continuant')], {
            (entity, 'Continuant', 'CLASSIFIES', entity, 'Spec Atom', True),
            (entity, 'Continuant', 'CLASSIFIES', entity, 'PMETA Atom', True),
        })
        for member, classification, levels in (
            ("Ticket Atom", "Continuant", ("model_entities", "model_entities")),
            ("Ephemeral", "SSOT", ("model_entities", "model_entities")),
            ("Spec Atom", "SSOT", ("instances", "model_entities")),
        ):
            with self.assertRaisesRegex(ValueError, "endpoint levels or kinds"):
                self.endpoint("IS_CLASSIFIED_BY", member, classification, levels=levels)


if __name__ == "__main__":
    unittest.main(verbosity=2)
