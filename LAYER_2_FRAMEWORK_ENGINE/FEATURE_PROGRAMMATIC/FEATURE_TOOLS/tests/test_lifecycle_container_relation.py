"""Check Container Relations against declared endpoint kinds and rules."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ATOM_LIFECYCLE.common import InputError
from ATOM_LIFECYCLE.container_relation import validate_container_relation
from FEATURE_MODEL.FEATURE_GENERATED_MODEL import Atom, Continuant, Node, Operations, ScopeUnit, Step, Workflow


class ContainerRelationTests(unittest.TestCase):
    def setUp(self):
        self.selection = SimpleNamespace(
            settings={"artifacts": {"identity": {"project_prefix": "CA"}}},
            structure={"scope_units": [{"scope_unit_name": "TEST", "scope_unit_id": "CA-SU-00",
                                        "parent": "PROJECT"}]},
        )
        self.paths = {
            "Node": "Node", "Node/Continuant": "Continuant", "Atom": "Atom", "Scope Unit": "ScopeUnit",
            "Atom/(.Header.Context.Role:=Operations)": "Operations",
            "Atom/(.Header.Context.Role:=Operations)/Step": "Step",
            "Atom/(.Header.Context.Role:=Operations)/Workflow": "Workflow",
        }
        classes = (Node, Continuant, Atom, ScopeUnit, Operations, Step, Workflow)
        rules = {
            "endpoints": {"IS_CONTAINED_BY": {
                "relation_name": "IS_CONTAINED_BY",
                "source_endpoint": {"level": "instances", "entity_paths": ["Atom"]},
                "target_endpoint": {"level": "instances", "entity_paths": ["Atom", "Scope Unit"]},
            }},
            "kinds": self.paths,
            "entity_rules": {kind.__name__: {} for kind in classes},
        }
        rules["entity_rules"]["Atom"]["IS_CONTAINED_BY"] = {"targets_per_source": 1}
        rules["entity_rules"]["Step"]["IS_CONTAINED_BY"] = {
            "target_entity_paths": ["Atom/(.Header.Context.Role:=Operations)/Workflow",
                                    "Atom/(.Header.Context.Role:=Operations)/Step"],
            "targets_per_source": 1,
        }
        schema = SimpleNamespace(header_relation_rules=rules, role_form=SimpleNamespace(decode=lambda _, value: value))
        self.model = SimpleNamespace(candidate_schema=schema)

    def test_scope_and_bootstrap(self):
        for ref in ("CA-SU-00", "TEST", "CA-SU--1"):
            with self.subTest(ref=ref):
                validate_container_relation(self.selection, self.model, {
                    "role": "Requirement", "form": "Declaration", "container": {"scope_unit": ref},
                })
        with self.assertRaisesRegex(InputError, "missing or ambiguous"):
            validate_container_relation(self.selection, self.model, {
                "role": "Requirement", "form": "Declaration", "container": {"scope_unit": "CA-SU-99"},
            })

    def test_step_container_applies_inherited_and_local_constraints(self):
        child = {"role": "Operations", "form": "Step", "container": {"atom": "CA-O-1"}}
        pin = SimpleNamespace(metadata={"role": "Operations", "form": "Workflow"})
        with patch("ATOM_LIFECYCLE.container_relation.select_current_sources", return_value={"CA-O-1": pin}):
            validate_container_relation(self.selection, self.model, child)
            pin.metadata["form"] = "Action"
            with self.assertRaisesRegex(InputError, "invalid target kind"):
                validate_container_relation(self.selection, self.model, child)
        with self.assertRaisesRegex(InputError, "invalid target kind"):
            validate_container_relation(self.selection, self.model, child | {"container": {"scope_unit": "TEST"}})

    def test_older_assets_leave_existing_behavior_in_place(self):
        model = SimpleNamespace(candidate_schema=SimpleNamespace(header_relation_rules=None))
        validate_container_relation(self.selection, model, {})

    def test_real_project_selects_current_container_atom(self):
        from ATOM_LIFECYCLE.placement_model import bind_placement
        from lifecycle_placement_test_support import fixture_rules
        from project_selection import resolve_project
        from scope_declaration_test_support import write_scope_unit_declarations

        with TemporaryDirectory() as directory, bind_placement(fixture_rules()):
            root = Path(directory).resolve()
            control = root / ".caprmedio_test"
            control.mkdir()
            (control / "caprmedio_project_settings.toml").write_text(
                '[project]\nname="TEST"\n[artifacts.identity]\nproject_prefix="CA"\n'
                '[paths]\ncontrol_root=".caprmedio_test"\n'
            )
            write_scope_unit_declarations(root, control_root=control)
            folder = control / "09_operations"
            folder.mkdir()
            (folder / "CA-O-1-WORKFLOW--example.md").write_text(
                '---\natom_id: CA-O-1\nrole: Operations\nform: Workflow\n'
                'status: Active\nversion: 1\n---\n\n## Summary\n\nExample\n'
            )
            view = {"role": "Operations", "form": "Step", "container": {"atom": "CA-O-1"}}
            validate_container_relation(resolve_project(root), self.model, view)


if __name__ == "__main__":
    unittest.main()
