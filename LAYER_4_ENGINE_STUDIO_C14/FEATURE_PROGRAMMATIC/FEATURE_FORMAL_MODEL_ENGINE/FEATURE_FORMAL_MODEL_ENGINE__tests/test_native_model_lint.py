"""Native Formal Claim linting uses the supplied Model catalog."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROGRAMMATIC = Path(__file__).resolve().parents[2]
from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.lint_python_model_claim__pub import lint_python_model_claim


class NativeModelLintTests(unittest.TestCase):
    def lint(self, source, *, addresses=("Atom", "Atom.Content", "Scope Unit", "Carrier"),
             relations=("IS_PROPERTY_OF", "IS_CONTAINED_BY"), bindings=None):
        return lint_python_model_claim(source, declared_addresses=addresses, relation_names=relations,
                                       path="atom.md", first_line=10, python_class_bindings=bindings)

    def test_native_field_contracts_are_checked_without_compiler(self):
        source = ("from dataclasses import dataclass, field\n"
                  "from anechoic.formal_claims import declare_entity\n"
                  "@dataclass\nclass Example:\n"
                  "    id: int = field(metadata={'property_occurrence_cardinality': 1, 'value_cardinality': 1})\n"
                  "declare_entity(entity_name='Example', entity_class=Example)\n")
        with patch('FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE.compiler_claim.compiler_model_statements', side_effect=AssertionError('translated')):
            self.assertEqual((), self.lint(source))
            for modified, message in (
                (source.replace('    id: int', '    extra: str\n    id: int'), 'unsupported dataclass field contract'),
                (source.replace("'value_cardinality': 1", "'other': 1"), 'require occurrence and value cardinalities'),
                (source.replace('id: int', 'id: list[int]'), 'unsupported compiler format'),
                (source.replace("entity_class=Example)", "entity_class=Example, classifications={'Container': 'yes'})"), 'unsupported dataclass field contract declaration'),
            ):
                with self.subTest(message=message):
                    self.assertIn(message, self.lint(modified)[0])

    def test_current_workspace_and_view_field_contracts(self):
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.ADAPTERS_C30__shared import iter_formal_claims as _native_block
        root = Path(__file__).parent / 'assets'
        for number in (2792, 2793):
            path = next(root.glob(f'CA-R-{number}-*.md'))
            source = next(_native_block(path.read_text()))
            with self.subTest(number=number):
                self.assertEqual((), self.lint(source, addresses=('View', 'Workspace'), relations=('IS_CONTAINED_BY',)))

    def test_property_references_and_missing_bearer(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "declare_entity(entity_name='Claim', relation_name='IS_PROPERTY_OF', "
                  "base_path='Atom.Content', value_format=str)")
        self.assertEqual(self.lint(source), ())
        self.assertIn("unknown Model address: Atom.Content", self.lint(source, addresses=("Atom",))[0])
        self.assertIn("unknown Relation: IS_PROPERTY_OF", self.lint(source, relations=())[0])

    def test_class_base_is_a_declared_model_class(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import ScopeUnit\n"
                  "class Project(ScopeUnit):\n    pass\n"
                  "declare_entity(entity_class=Project, entity_name='Project')")
        self.assertEqual(self.lint(source), ())
        self.assertIn("unknown Model class: ScopeUnit", self.lint(source, addresses=("Atom",))[0])

    def test_instance_check_type_uses_declared_model_catalog(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import ScopeUnit\n"
                  "def check(unit: ScopeUnit) -> bool:\n    return unit.id != 'CA-SU--1'\n"
                  "declare_entity(entity_name='Scope Unit', instance_check=check)")
        self.assertEqual(self.lint(source), ())
        self.assertIn("unknown Model class: ScopeUnit", self.lint(source, addresses=("Atom",))[0])

    def test_instance_check_must_match_the_declared_class(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import ScopeUnit\n"
                  "class Project(ScopeUnit):\n    pass\n"
                  "def check(unit: ScopeUnit) -> bool:\n    return True\n"
                  "declare_entity(entity_class=Project, entity_name='Project', instance_check=check)")
        self.assertIn("instance check argument must match entity_class", self.lint(source)[0])

    def test_qualified_class_imports_must_be_unambiguous(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import Decision\n"
                  "class Detail(Decision):\n    pass\n"
                  "declare_entity(entity_class=Detail, entity_name='Detail')")
        decision = "Atom/(.Header.Context.Role := Method)/(.Header.Context.Form := Decision)"
        other = "Atom/(.Header.Context.Role := Evaluation)/(.Header.Context.Form := Decision)"
        self.assertEqual(self.lint(source, addresses=(decision,)), ())
        self.assertIn("ambiguous Model class: Decision", self.lint(source, addresses=(decision, other))[0])

    def test_exact_python_class_binding_selects_qualified_model_identity(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import Requirement\n"
                  "class R(Requirement):\n    pass\n"
                  "declare_entity(entity_class=R, entity_name='R')")
        role = "Atom/(.Header.Context.Role := Requirement)"
        form = "Atom/(.Header.Context.Form := Requirement)"
        addresses = (role, form)
        self.assertIn("ambiguous Model class", self.lint(source, addresses=addresses)[0])
        self.assertEqual(self.lint(source, addresses=addresses, bindings={"Requirement": [role]}), ())
        self.assertIn("ambiguous Model class", self.lint(
            source, addresses=addresses, bindings={"Requirement": [role, form]})[0])
        self.assertIn("unknown Model class address", self.lint(
            source, addresses=(form,), bindings={"Requirement": [role]})[0])
        self.assertIn("ambiguous Model class", self.lint(source, addresses=addresses, bindings={})[0])

    def test_graph_catalog_resolves_unambiguous_legacy_imports(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "from anechoic.model import ScopeUnit\n"
                  "class Project(ScopeUnit):\n    pass\n"
                  "declare_entity(entity_class=Project, entity_name='Project')")
        self.assertEqual(self.lint(source, addresses=("Scope Unit",), bindings={}), ())
        self.assertIn("unknown Model class", self.lint(source, addresses=("Atom",), bindings={})[0])
        self.assertIn("unknown Model class address", self.lint(
            source, addresses=("Scope Unit",), bindings={"ScopeUnit": ["Atom"]})[0])

    def test_graph_catalog_supports_legacy_claims_with_qualified_entries(self):
        addresses = ("Atom", "Atom.Content", "Atom/(.Header.Context.Role:=Requirement)")
        self.assertEqual(self.lint("property_rule(address='Atom.Content', values='1')", addresses=addresses,
                                   bindings={"Requirement": [addresses[-1]]}), ())

    def test_relation_endpoints_are_checked(self):
        source = ("from anechoic.formal_claims import declare_relation\n"
                  "declare_relation(relation_name='TEST', "
                  "source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)}, "
                  "target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)})")
        self.assertEqual(self.lint(source), ())
        self.assertIn("unknown Model address: Carrier", self.lint(source, addresses=("Atom",))[0])

    def test_property_accepts_exact_qualified_bearer(self):
        path = "Atom/(.Header.Context.Role:=Operations)/Step.Content.Claim"
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "declare_entity(entity_name='Mermaid Scheme', relation_name='IS_PROPERTY_OF', "
                  f"base_path={path!r})")
        self.assertEqual(self.lint(source, addresses=(path,)), ())
        self.assertTrue(self.lint(source, addresses=(path.replace("Operations", "Method"),)))

    def test_model_and_instance_relation_constraints_are_checked(self):
        for level in ("model", "instance"):
            with self.subTest(level=level):
                prefix = ("from anechoic.formal_claims import declare_entity\n"
                          f"declare_entity(entity_name='Project', {level}_relation_constraints=")
                valid = prefix + "{'IS_CONTAINED_BY': {'target_entity_paths': ('Scope Unit',)}})"
                self.assertEqual(self.lint(valid), ())
                self.assertIn("unknown Relation", self.lint(valid, relations=())[0])
                self.assertIn("unknown Model address", self.lint(valid, addresses=("Atom",))[0])
                malformed = prefix + "{'IS_CONTAINED_BY': 'invalid'})"
                self.assertIn("must map Relation names", self.lint(malformed)[0])

    def test_invalid_native_code_has_location_and_is_never_executed(self):
        source = ("from anechoic.formal_claims import declare_entity\n"
                  "declare_entity(entity_name=__import__('os').getcwd())")
        diagnostic = self.lint(source)[0]
        self.assertIn("atom.md:11:", diagnostic)
        self.assertIn("unsupported expression", diagnostic)

    def test_cli_loads_native_parser_without_project_pythonpath(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claim = root / "claim.md"
            addresses = root / "addresses.json"
            relations = root / "relations.json"
            claim.write_text("## Claim\n### Formal Claim\n```python\n"
                             "from anechoic.formal_claims import declare_entity\n"
                             "declare_entity(entity_name='Name', relation_name='IS_PROPERTY_OF', "
                             "base_path='Atom')\n```\n")
            addresses.write_text(json.dumps(["Atom"]))
            relations.write_text(json.dumps(["IS_PROPERTY_OF"]))
            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            result = subprocess.run([sys.executable, "-B", str(PROGRAMMATIC / "FEATURE_FORMAL_MODEL_ENGINE" /
                                                       "lint_python_model_claim__pub.py"), str(claim),
                                     "--addresses", str(addresses), "--relations", str(relations)],
                                    capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_accepts_model_catalog_with_explicit_python_classes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claim, addresses, relations = (root / name for name in ("claim.py", "addresses.json", "relations.json"))
            claim.write_text("from anechoic.formal_claims import declare_entity\n"
                             "from anechoic.model import Requirement\n"
                             "class R(Requirement):\n    pass\n"
                             "declare_entity(entity_class=R, entity_name='R')\n")
            role = "Atom/(.Header.Context.Role:=Requirement)"
            addresses.write_text(json.dumps({"addresses": [role], "python_classes": {"Requirement": [role]}}))
            relations.write_text("[]")
            result = subprocess.run([sys.executable, "-B", str(PROGRAMMATIC / "FEATURE_FORMAL_MODEL_ENGINE" /
                                                       "lint_python_model_claim__pub.py"), str(claim),
                                     "--addresses", str(addresses), "--relations", str(relations)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
