"""Separate Primary and Property declarations compile into public classes."""

import importlib
from dataclasses import asdict
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_classes, assemble_model_modules


def primary(name, base=None, entity_name=None, extra=""):
    imports = f"from anechoic.model import {base}\n" if base else ""
    return ("from anechoic.formal_claims import declare_entity\n" + imports
            + f"class {name}{f'({base})' if base else ''}:\n    pass\n"
            + f"declare_entity(entity_name={entity_name or name!r}, entity_class={name}, entity_kind='Primary'{extra})\n")


def prop(name, base, extra=""):
    return ("from anechoic.formal_claims import declare_entity\nfrom datetime import datetime\n"
            + f"declare_entity(entity_name={name!r}, entity_kind='Property', relation_name='IS_PROPERTY_OF', "
            + f"base_path={base!r}{extra})\n")


class ManifestPropertyFieldsTests(unittest.TestCase):
    def claims(self):
        atom = "Node//Artifact//Atom"
        return [primary("Node"), primary("Artifact", "Node"),
                primary("Atom", "Artifact", extra=", identity_properties=('Identity.Atom ID',)"),
                primary("Plan", "Atom", extra=", identity_properties=('State.Version',)"),
                prop("Identity", atom, ", value_cardinality=0, allowed_dependent_property_names=('Atom ID',)"),
                prop("Atom ID", atom + ".Identity", ", value_format=str"),
                prop("State", atom, ", value_cardinality=0, "
                     "allowed_dependent_property_names=('Version', 'Status', 'Updated At')"),
                prop("Version", atom + ".State", ", value_format=int, minimum_value=1"),
                prop("Status", atom + ".State", ", value_format=str, "
                     "field_options={'kw_only': True}, allowed_values=('draft', 'active')"),
                prop("Updated At", atom + ".State", ", value_format=datetime"),
                prop("Tags", atom, ", value_format=list[str] | None, field_options={'default': None, 'kw_only': True}"),
                prop("Attributes", atom, ", value_format=dict[str, str], field_options={'default_factory': dict, 'kw_only': True}"),
                prop("Ref ID", atom, ", value_format=str, "
                     "derived_from_properties=('Identity.Atom ID', 'State.Version', 'State.Status')"),
                prop("Status", atom + ".State", ", applies_to_entity_classes=('Node//Artifact//Atom//Plan',), "
                     "allowed_values=('draft', 'active', 'done')")]

    def test_aggregate_and_modules_emit_fields_on_correct_classes(self):
        claims = self.claims()
        modules = assemble_model_modules(claims)
        self.assertIn("class Atom(Artifact)", modules["atom.py"])
        self.assertIn("class Plan(Atom)", modules["plan.py"])
        self.assertNotIn("version:", modules["plan.py"])
        with TemporaryDirectory() as folder:
            package = Path(folder) / "model_fixture"
            package.mkdir()
            (package / "__init__.py").write_text("")
            for filename, source in modules.items():
                (package / filename).write_text(source)
            with patch.object(sys, "path", [folder, *sys.path]):
                try:
                    atom = importlib.import_module("model_fixture.atom").Atom
                    plan = importlib.import_module("model_fixture.plan").Plan
                    self.assertTrue(issubclass(plan, atom))
                    self.assertEqual(set(atom.__dataclass_fields__),
                                     {"atom_id", "version", "status", "updated_at", "tags", "attributes"})
                    self.assertEqual(atom.__dataclass_fields__["version"].metadata["minimum_value"], 1)
                    self.assertEqual(plan.__dataclass_fields__["status"].metadata["allowed_values"], ("draft", "active", "done"))
                    self.assertIs(atom.__dataclass_fields__["attributes"].default_factory, dict)
                    self.assertTrue(atom.__dataclass_fields__["tags"].kw_only)
                    from datetime import datetime
                    values = {"atom_id": "AN-S-1", "version": 2, "updated_at": datetime.now()}
                    instance = plan(**values, status="draft")
                    self.assertEqual(instance.ref_id, "AN-S-1@2-draft")
                    instance.status = "active"
                    self.assertEqual(instance.ref_id, "AN-S-1@2")
                    instance.version = 3
                    instance.status = "archived"
                    self.assertEqual(instance.ref_id, "AN-S-1@3")
                    self.assertNotIn("ref_id", asdict(instance))
                    self.assertNotIn("ref_id", vars(instance))
                    with self.assertRaises(AttributeError):
                        instance.ref_id = "incorrect"
                    with self.assertRaisesRegex(TypeError, "ref_id"):
                        atom(**values, status="active", ref_id="incorrect")
                finally:
                    for name in list(sys.modules):
                        if name == "model_fixture" or name.startswith("model_fixture."):
                            del sys.modules[name]

    def test_rejects_non_primary_class_and_invalid_overrides(self):
        claims = self.claims()
        with self.assertRaisesRegex(ValueError, "whitelisted"):
            assemble_model_classes(claims + [primary("Bad", extra=", instance_population_cardinality=1")])
        with self.assertRaisesRegex(ValueError, "subclass"):
            assemble_model_classes(claims + [prop("Atom ID", "Node//Artifact//Atom.Identity", ", applies_to_entity_classes=('Node',)")])
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            assemble_model_classes(claims + [primary("Other", entity_name="Atom")])
        with self.assertRaisesRegex(ValueError, "State: expected declared children"):
            assemble_model_classes([claim for claim in claims if "entity_name='Updated At'" not in claim])
        with self.assertRaisesRegex(ValueError, "State: expected declared children"):
            assemble_model_classes([claim.replace("('Version', 'Status', 'Updated At')", "('Version', 'Status')")
                                    for claim in claims])
        with self.assertRaisesRegex(ValueError, "must be declared at State"):
            assemble_model_classes(claims + [prop("UpdatedAt", "Node//Artifact//Atom", ", value_format=datetime")])
        with self.assertRaisesRegex(ValueError, "identity Property does not exist"):
            assemble_model_classes([primary("Base", extra=", identity_properties=('Missing',)")])
        with self.assertRaisesRegex(ValueError, "requires its derived"):
            assemble_model_classes([claim.replace(", derived_from_properties=('Identity.Atom ID', 'State.Version', 'State.Status')", "")
                                    for claim in claims])
        with self.assertRaisesRegex(ValueError, "cannot be redeclared"):
            assemble_model_classes(claims + [prop("Ref ID", "Node//Artifact//Atom//Plan", ", value_format=str")])

    def test_identity_resolves_every_segment_from_the_primary_entity(self):
        claims = self.claims()
        for path in ("Atom ID", "Imaginary.Atom ID", "State.Atom ID", "Atom.Identity.Atom ID"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "identity Property does not exist"):
                assemble_model_classes([claim.replace("identity_properties=('Identity.Atom ID',)",
                                                     f"identity_properties=({path!r},)") for claim in claims])
        nested = [primary("Entity", extra=", identity_properties=('Identity.Revision.Version',)"),
                  prop("Identity", "Entity", ", value_cardinality=0, allowed_dependent_property_names=('Revision',)"),
                  prop("Revision", "Entity.Identity", ", value_cardinality=0, allowed_dependent_property_names=('Version',)"),
                  prop("Version", "Entity.Identity.Revision", ", value_format=int")]
        self.assertIn("version: int", assemble_model_classes(nested))
        with self.assertRaisesRegex(ValueError, "Unresolved Property group bearer"):
            assemble_model_classes([nested[0], nested[1], nested[3]])

    def test_header_paths_and_inherited_group(self):
        atom = "Node//Artifact//Atom"
        spec = atom + "//SpecAtom"
        claims = [primary("Node"), primary("Artifact", "Node"),
                  primary("Atom", "Artifact", extra=", identity_properties=('Header.Atom ID',)"),
                  primary("SpecAtom", "Atom"),
                  prop("Header", atom, ", value_cardinality=0, "
                       "allowed_dependent_property_names=('Atom Family', 'Atom ID', 'State', 'Structure')"),
                  prop("Atom Family", atom + ".Header", ", value_format=str, allowed_values=('SPEC', 'TKT', 'PROJECT_CONFIG')"),
                  prop("Atom ID", atom + ".Header", ", value_format=str"),
                  prop("State", atom + ".Header", ", value_cardinality=0, allowed_dependent_property_names=('Version', 'Status', 'Updated At')"),
                  prop("Version", atom + ".Header.State", ", value_format=int"),
                  prop("Status", atom + ".Header.State", ", value_format=str"),
                  prop("Updated At", atom + ".Header.State", ", value_format=datetime"),
                  prop("Structure", atom + ".Header", ", value_cardinality=0, allowed_dependent_property_names=('Tier',)"),
                  prop("Tier", spec + ".Header.Structure", ", value_format=int"),
                  prop("Ref ID", atom, ", value_format=str, derived_from_properties=('Header.Atom ID', 'Header.State.Version', 'Header.State.Status')")]
        namespace = {}
        exec(assemble_model_classes(claims), namespace)
        from datetime import datetime
        values = dict(atom_id="AN-S-1", version=2, status="draft", updated_at=datetime.now(), tier=3)
        instance = namespace["SpecAtom"](atom_family="SPEC", **values)
        self.assertEqual(instance.ref_id, "AN-S-1@2-draft")
        self.assertNotIn("ref_id", asdict(instance))
        namespace["SpecAtom"](atom_family="PROJECT_CONFIG", **(values | {"atom_id": "AN-P-1"}))
        with self.assertRaisesRegex(ValueError, "Atom Family disagrees"):
            namespace["SpecAtom"](atom_family="PMETA", **(values | {"atom_id": "AN-P-1"}))
        with self.assertRaisesRegex(ValueError, "Atom Family disagrees"):
            namespace["SpecAtom"](atom_family="TKT", **values)
        with self.assertRaisesRegex(ValueError, "Unresolved Property group bearer"):
            assemble_model_classes([claim.replace(spec + ".Header.Structure", spec + ".Header.Missing") for claim in claims])
        with self.assertRaisesRegex(ValueError, "Duplicate inherited Property field"):
            assemble_model_classes(claims + [prop("Version", spec + ".Header.Structure", ", value_format=int")])
        with self.assertRaisesRegex(ValueError, "Unresolved Property group bearer"):
            assemble_model_classes([claim.replace(atom + ".Header.State", atom + ".State")
                                    if "entity_name='Version'" in claim else claim for claim in claims])

    def test_override_replaces_default_options(self):
        claims = [primary("Base"), primary("Child", "Base"),
                  prop("Name", "Base", ", value_format=str, field_options={'default': 'x', 'kw_only': True}"),
                  prop("Name", "Base", ", applies_to_entity_classes=('Base//Child',), field_options={}")]
        namespace = {}
        exec(assemble_model_classes(claims), namespace)
        field = namespace["Child"].__dataclass_fields__["name"]
        self.assertFalse(field.kw_only)
        self.assertIs(field.default, __import__("dataclasses").MISSING)

    def test_class_var_and_mixed_layout(self):
        claims = [primary("Base"), prop("URL Value", "Base", ", value_format=str, "
                                      "field_options={'class_var': True, 'default': 'value'}")]
        module = ModuleType("manifest_classvar_fixture")
        with patch.dict(sys.modules, {module.__name__: module}):
            exec(assemble_model_classes(claims), vars(module))
            self.assertEqual(module.Base.url_value, "value")
            self.assertEqual(__import__("dataclasses").fields(module.Base), ())
        with self.assertRaisesRegex(ValueError, "requires entity_kind"):
            assemble_model_classes(claims + [prop("Other", "Base", ", value_format=str")
                                   .replace("entity_kind='Property', ", "")])

    def test_fields_are_sorted_required_first_and_independent_of_claim_order(self):
        claims = [primary("Base"), prop("Optional", "Base", ", value_format=str, field_options={'default': 'x'}"),
                  prop("Required", "Base", ", value_format=str")]
        source = assemble_model_classes(claims)
        self.assertEqual(source, assemble_model_classes(reversed(claims)))
        self.assertEqual(assemble_model_modules(claims), assemble_model_modules(reversed(claims)))
        namespace = {}
        exec(source, namespace)
        self.assertEqual(namespace["Base"]("value").required, "value")
        self.assertEqual(assemble_model_modules(self.claims()), assemble_model_modules(reversed(self.claims())))


if __name__ == "__main__":
    unittest.main()
