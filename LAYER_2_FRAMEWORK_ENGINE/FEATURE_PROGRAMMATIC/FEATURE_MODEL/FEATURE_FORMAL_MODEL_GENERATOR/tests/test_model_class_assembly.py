"""Class assembly uses native Python inheritance without executing Claims."""

from graphlib import CycleError
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from unittest.mock import patch

PROGRAMMATIC = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROGRAMMATIC))

from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_class_assembly import assemble_model_classes, build_model_class_source
from FEATURE_MODEL.FEATURE_FORMAL_MODEL_GENERATOR.model_declaration_sources import select_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_declaration_bindings import bind_model_declarations
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.model_field_validation import validate_model_fields
from FEATURE_MODEL.FEATURE_MODEL_VALIDATION.validate_model_instance import validate_model_instance
from FEATURE_FORMAL_MODEL_ENGINE.native_model_claim import parse_native_model_claim


def declaration(name, parent=None):
    base_import = f"from caprmedio.model import {parent}\n" if parent else ""
    base = f"({parent})" if parent else ""
    return ("from caprmedio.formal_claims import declare_entity\n"
            "from dataclasses import dataclass\n" + base_import +
            f"@dataclass\nclass {name}{base}:\n    pass\n"
            f"declare_entity(entity_name='{name}', entity_class={name})\n")


class ModelClassAssemblyTests(unittest.TestCase):
    def test_generated_atom_composes_header_context_and_content(self):
        from FEATURE_MODEL.FEATURE_GENERATED_MODEL import Atom, AtomHeader, AtomContext, AtomContent, AtomTier, Plan

        self.assertEqual(set(Atom.__dataclass_fields__), {"header", "content"})
        self.assertEqual(set(AtomHeader.__dataclass_fields__), {"identity", "context", "relations", "state", "destination"})
        self.assertEqual(set(AtomContext.__dataclass_fields__),
                         {"container", "role", "form", "label", "topics", "tier", "plan", "concern"})
        self.assertEqual(set(AtomContent.__dataclass_fields__), {"summary", "properties"})
        self.assertEqual(set(AtomTier.__dataclass_fields__), {"value", "label"})
        relation = AtomHeader.__dataclass_fields__["relations"].metadata
        self.assertEqual(relation["dependent_property_value_cardinality"], {"minimum": 1, "maximum": None})
        self.assertTrue(issubclass(Plan, Atom))

    def test_atom_state_fields_and_bound_come_from_property_declarations(self):
        imports = "from caprmedio.formal_claims import declare_entity\n"
        group = imports + (
            "declare_entity(entity_name='State', relation_name='IS_PROPERTY_OF', base_path='Atom.Header', "
            "property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=1, "
            "allowed_dependent_property_names=('Version',))"
        )
        version = imports + (
            "declare_entity(entity_name='Version', relation_name='IS_PROPERTY_OF', base_path='Atom.Header.State', "
            "property_occurrence_cardinality=1, value_cardinality=1, dependent_property_cardinality=0, "
            "value_format=int, minimum_value=2)"
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / 'atom_state_fixture.py'
            path.write_text(assemble_model_classes([group, version]))
            spec = spec_from_file_location(path.stem, path)
            module = module_from_spec(spec)
            with patch.dict(sys.modules, {path.stem: module}):
                spec.loader.exec_module(module)
                validate_model_fields(module.AtomState, {"version": 2})
                with self.assertRaisesRegex(ValueError, "version: value must be at least 2"):
                    validate_model_fields(module.AtomState, {"version": 1})
                with self.assertRaisesRegex(ValueError, "version:"):
                    validate_model_fields(module.AtomState, {"version": True})
        with self.assertRaisesRegex(ValueError, "expected the declared scalar Properties"):
            assemble_model_classes([group])

    def test_inheritance_is_ordered_and_importable(self):
        source = assemble_model_classes([declaration("Project", "ScopeUnit"), declaration("ScopeUnit")])
        namespace = {}
        exec(compile(source, "model.py", "exec"), namespace)
        self.assertTrue(issubclass(namespace["Project"], namespace["ScopeUnit"]))
        self.assertNotIn("caprmedio.model", source)

    def test_missing_parent_and_cycle_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing Model parent"):
            assemble_model_classes([declaration("Project", "ScopeUnit")])
        with self.assertRaises(CycleError):
            assemble_model_classes([declaration("A", "B"), declaration("B", "A")])

    def test_invalid_inherited_dataclass_fields_fail_at_build(self):
        parent = declaration("Parent").replace("    pass", "    optional: str = ''")
        child = declaration("Child", "Parent").replace("    pass", "    required: str")
        with self.assertRaisesRegex(TypeError, "non-default argument"):
            assemble_model_classes([child, parent])

    def test_build_selects_current_model_declarations_before_assembly(self):
        def carrier(name, namespace, claim):
            return {
                "source": {"path": name + ".md", "atom_id": name},
                "read_view": {"status": "active", "content_role": "Requirement"},
                "subjects": {"governs": f"{namespace} <+ {name}"},
                "body": f"## Claim\n### Formal Claim\n```python\n{claim}```\n",
            }
        source = build_model_class_source([
            carrier("Project", "CAPRMEDIO_MODEL", declaration("Project", "ScopeUnit")),
            carrier("ScopeUnit", "CAPRMEDIO_MODEL", declaration("ScopeUnit")),
            carrier("Engine", "CAPRMEDIO_STRUCTURE", "invalid Python\n"),
        ])
        namespace = {}
        exec(source, namespace)
        self.assertTrue(issubclass(namespace["Project"], namespace["ScopeUnit"]))

    def test_legacy_and_duplicate_declarations_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "native Python"):
            assemble_model_classes(["property_rule(address='A')"])
        with self.assertRaisesRegex(ValueError, "Duplicate Model class"):
            assemble_model_classes([declaration("A"), declaration("A")])

    def test_plain_claim_class_becomes_dataclass(self):
        claim = (
            "from caprmedio.formal_claims import declare_entity\n"
            "class Item:\n    name: str\n"
            "declare_entity(entity_name='Item', entity_class=Item)\n"
        )
        namespace = {}
        exec(assemble_model_classes([claim]), namespace)
        self.assertEqual("hello", namespace["Item"]("hello").name)

    def test_quoted_annotation_is_rejected_before_runtime_type_resolution(self):
        claim = declaration("Item").replace("    pass", '    name: "open(\'file\', \'w\')"')
        with self.assertRaisesRegex(ValueError, "use an unquoted Python annotation"):
            assemble_model_classes([claim])

    def test_string_literal_values_are_preserved_in_types(self):
        claim = "from typing import Literal\n" + declaration("Item").replace(
            "    pass", '    label: Literal["Ready"]'
        )
        self.assertIn("Literal['Ready']", assemble_model_classes([claim]))

    def test_field_cardinality_is_materialized_without_a_claim_helper_import(self):
        claim = (
            "from dataclasses import dataclass, field\n"
            "from caprmedio.formal_claims import Cardinality, declare_entity\n"
            "@dataclass\nclass Item:\n"
            "    name: str = field(metadata={'values': Cardinality(minimum=1, maximum=1)})\n"
            "declare_entity(entity_name='Item', entity_class=Item)\n"
        )
        source = assemble_model_classes([claim])
        namespace = {}
        exec(source, namespace)
        self.assertNotIn("caprmedio.formal_claims", source)
        field = namespace["Item"].__dataclass_fields__["name"]
        self.assertEqual(field.metadata["values"], {"minimum": 1, "maximum": 1})

    def test_imported_class_validates_inherited_fields(self):
        claim = declaration("Base").replace("    pass", "    name: str")
        with TemporaryDirectory() as folder:
            path = Path(folder) / "model.py"
            path.write_text(assemble_model_classes([declaration("Child", "Base"), claim]))
            spec = spec_from_file_location("test_generated_model", path)
            module = module_from_spec(spec)
            with patch.dict(sys.modules, {spec.name: module}):
                spec.loader.exec_module(module)
                validate_model_fields(module.Child, {"name": "valid"})
                with self.assertRaises(ValueError):
                    validate_model_fields(module.Child, {"name": 1})

    def test_selected_declarations_drive_the_shared_validator(self):
        node_claim = declaration("Node").replace("    pass", "    identity: int").replace(
            "entity_class=Node)", "entity_class=Node, population_unique_constraints=({'keys': ('Identity',)},))"
        )
        property_claim = (
            "from caprmedio.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Identity', relation_name='IS_PROPERTY_OF', base_path='Node')\n"
        )
        relation_claim = (
            "from caprmedio.formal_claims import declare_relation\n"
            "declare_relation(relation_name='IS_PROPERTY_OF', "
            "source_endpoint={'level': 'model_entities'}, target_endpoint={'level': 'model_entities'})\n"
        )
        def carrier(subject, claim):
            return {
                "source": {"path": subject + ".md", "atom_id": subject},
                "read_view": {"status": "active", "content_role": "Requirement"},
                "subjects": {"governs": "CAPRMEDIO_MODEL <+ " + subject},
                "body": f"## Claim\n### Formal Claim\n```python\n{claim}```\n",
            }
        rows = [carrier("Node", node_claim), carrier("Node.Identity", property_claim),
                carrier("Relation//IS_PROPERTY_OF", relation_claim)]
        namespace = {}
        exec(build_model_class_source(rows), namespace)
        declarations = [(subject, parse_native_model_claim(claim))
                        for _, subject, claim in select_model_declarations(rows)]
        relations, model_types, populations = bind_model_declarations(declarations, namespace)
        node = namespace["Node"]
        args = {"properties": {"identity": 1}, "outgoing_relations": {}, "checks": {},
                "relation_declarations": relations, "model_types": model_types,
                "population_declarations": populations}
        self.assertEqual(validate_model_instance(node, population_peers={node: []}, **args), node(1))
        with self.assertRaisesRegex(ValueError, "Population uniqueness violated"):
            validate_model_instance(node, population_peers={node: [node(1)]}, **args)


if __name__ == "__main__":
    unittest.main()
