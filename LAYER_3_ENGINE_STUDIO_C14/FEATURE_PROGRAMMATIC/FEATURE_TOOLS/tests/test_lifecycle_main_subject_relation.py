"""Check Main Subject resolution and the Scope Unit Declaration constraint."""

from types import SimpleNamespace
from unittest.mock import patch
import unittest

from ATOM_LIFECYCLE.common import InputError
from ATOM_LIFECYCLE.main_subject_relation import validate_main_subject_relation


class MainSubjectRelationTests(unittest.TestCase):
    def setUp(self):
        self.selection = SimpleNamespace(structure={"scope_units": [
            {"scope_unit_name": "test", "parent": "PROJECT"},
            {"scope_unit_name": "TOOLS", "parent": "test"},
        ]})
        name = "HAS_ACTIVE_SUBJECT"
        rules = {
            "kinds": {
                "Atom": "Atom", "Scope Unit": "ScopeUnit",
                "Atom/(.Header.Context.Role:=Requirement)": "Requirement",
                "Atom/(.Header.Context.Role:=Requirement)/(.Header.Context.Form:=Scope Unit Declaration)":
                    "ScopeUnitDeclaration",
            },
            "subjects": {"Atom.Header.Context": "Node", "CFEL <+ Relation//SPECIALIZES": "Relation"},
            "entity_rules": {
                "Node": {}, "Continuant": {}, "Atom": {name: {"targets_per_source": 1}},
                "Requirement": {}, "ScopeUnitDeclaration": {name: {"target_entity_paths": ["Scope Unit"]}},
            },
            "endpoints": {name: {
                "relation_name": name,
                "source_endpoint": {"level": "instances", "entity_paths": ["Atom"]},
                "target_endpoint": {"level": "model_entities_or_instances"},
            }},
        }
        self.model = SimpleNamespace(candidate_schema=SimpleNamespace(header_relation_rules=rules))

    def check(self, subject, form="Declaration", strict=True):
        view = {"role": "Requirement", "form": form, "topics": {"main_subject": subject}}
        validate_main_subject_relation(self.selection, self.model, view, require_resolution=strict)

    def test_accepts_model_class_property_and_relation(self):
        for subject in ("Atom", "Atom.Header.Context", "CFEL <+ Relation//SPECIALIZES"):
            self.check("ANECHOIC_MODEL <+ " + subject)

    def test_scope_unit_declaration_checks_its_target_kind(self):
        form = "Scope Unit Declaration"
        self.check("ANECHOIC_STRUCTURE <+ Scope Unit//TOOLS", form)
        self.check("ANECHOIC_STRUCTURE <+ Project//test", form)
        with self.assertRaisesRegex(InputError, "Scope Unit instance"):
            self.check("ANECHOIC_MODEL <+ Atom", form)
        with self.assertRaisesRegex(InputError, "Scope Unit instance"):
            self.check("ANECHOIC_MODEL <+ Scope Unit", form)
        with self.assertRaisesRegex(InputError, "missing or ambiguous"):
            self.check("ANECHOIC_STRUCTURE <+ Project//TOOLS", form)

    def test_unknown_topic_is_rejected_when_authored(self):
        self.check("ANECHOIC_MODEL <+ Former Node", strict=False)
        with self.assertRaisesRegex(InputError, "one declared endpoint"):
            self.check("ANECHOIC_MODEL <+ Former Node")

    def test_new_project_local_aspect_must_be_declared(self):
        subject = "ANECHOIC_STRUCTURE <+ Aspects <+ Engineering"
        with patch("ATOM_LIFECYCLE.main_subject_relation.resolve_aspect", return_value=True) as lookup:
            self.check(subject)
            lookup.assert_called_once()
            lookup.return_value = False
            with self.assertRaisesRegex(InputError, "one declared endpoint"):
                self.check(subject)
        self.check(subject, strict=False)

    def test_project_structure_root_is_bound_to_selected_project(self):
        self.selection.settings = {"project": {"name": "test"}}
        self.check("PROJECT STRUCTURE//test")
        with self.assertRaisesRegex(InputError, "one declared endpoint"):
            self.check("PROJECT STRUCTURE//other <+ Projection//Unbound")

    def test_structure_scope_resolves_full_selected_containment(self):
        self.selection.structure["scope_units"] = [
            {"scope_unit_name": "anechoic", "parent": "PROJECT"},
            {"scope_unit_name": "PARENT", "parent": "anechoic"},
            {"scope_unit_name": "CHILD", "parent": "PARENT"},
        ]
        form = "Scope Unit Declaration"
        self.check("ANECHOIC_STRUCTURE", form)
        self.check("ANECHOIC_STRUCTURE/PARENT/CHILD", form)
        with self.assertRaisesRegex(InputError, "one declared endpoint"):
            self.check("ANECHOIC_STRUCTURE/WRONG/CHILD", form)
        self.selection.structure["scope_units"].append({"scope_unit_name": "CHILD", "parent": "PARENT"})
        with self.assertRaisesRegex(InputError, "one declared endpoint"):
            self.check("ANECHOIC_STRUCTURE/PARENT/CHILD", form)
