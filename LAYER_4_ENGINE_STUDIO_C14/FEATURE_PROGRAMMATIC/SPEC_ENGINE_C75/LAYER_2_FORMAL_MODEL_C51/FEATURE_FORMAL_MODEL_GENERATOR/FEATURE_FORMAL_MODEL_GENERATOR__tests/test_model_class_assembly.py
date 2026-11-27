"""Class assembly uses native Python inheritance without executing Claims."""

from dataclasses import asdict, fields, is_dataclass
from graphlib import CycleError
from pathlib import Path
import sys
import importlib
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest

from pydantic import ValidationError
from pydantic.dataclasses import is_pydantic_dataclass
from importlib.util import module_from_spec, spec_from_file_location
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_FORMAL_MODEL_GENERATOR.\
    FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    assemble_model_classes,
    assemble_model_modules,
    build_model_class_source,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    validate_model_instance,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_MODEL_VALIDATION.model_field_validation import (
    validate_model_fields,
)  # fmt: skip


def declaration(name, parent=None):
    base_import = f"from anechoic.model import {parent}\n" if parent else ""
    base = f"({parent})" if parent else ""
    return (
        "from anechoic.formal_claims import declare_entity\n"
        "from dataclasses import dataclass\n"
        + base_import
        + f"@dataclass\nclass {name}{base}:\n    pass\n"
        f"declare_entity(entity_name='{name}', entity_class={name})\n"
    )


class ModelClassAssemblyTests(unittest.TestCase):
    def test_atom_state_fields_and_bound_come_from_property_declarations(self):
        imports = "from anechoic.formal_claims import declare_entity\n"
        group = imports + (
            "declare_entity(entity_name='State', "
            "relation_name='IS_PROPERTY_OF', base_path='Atom.Header', "
            "property_occurrence_cardinality=1, "
            "value_cardinality=0, dependent_property_cardinality=1, "
            "allowed_dependent_property_names=('Version',))"
        )
        version = imports + (
            "declare_entity(entity_name='Version', "
            "relation_name='IS_PROPERTY_OF', base_path='Atom.Header.State', "
            "property_occurrence_cardinality=1, "
            "value_cardinality=1, dependent_property_cardinality=0, "
            "value_format=int, minimum_value=2)"
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "atom_state_fixture.py"
            path.write_text(assemble_model_classes([group, version]))
            spec = spec_from_file_location(path.stem, path)
            module = module_from_spec(spec)
            with patch.dict(sys.modules, {path.stem: module}):
                spec.loader.exec_module(module)
                validate_model_fields(module.AtomState, {"version": 2})
                with self.assertRaisesRegex(
                    ValueError, "version: value must be at least 2"
                ):
                    validate_model_fields(module.AtomState, {"version": 1})
                with self.assertRaisesRegex(ValueError, "version:"):
                    validate_model_fields(module.AtomState, {"version": True})
        with self.assertRaisesRegex(
            ValueError, "expected the declared scalar Properties"
        ):
            assemble_model_classes([group])

    def test_inheritance_is_ordered_and_importable(self):
        source = assemble_model_classes(
            [declaration("Project", "ScopeUnit"), declaration("ScopeUnit")]
        )
        namespace = {}
        exec(compile(source, "model.py", "exec"), namespace)
        self.assertTrue(
            issubclass(namespace["Project"], namespace["ScopeUnit"])
        )
        self.assertNotIn("anechoic.model", source)

    def test_modules_are_deterministic_and_importable_with_dependencies(self):
        parent = declaration("ScopeUnit").replace("    pass", "    name: str")
        child = "from typing import Literal\n" + declaration(
            "Project", "ScopeUnit"
        ).replace("    pass", "    status: Literal['Ready'] = 'Ready'")
        modules = assemble_model_modules([child, parent])
        self.assertEqual(modules, assemble_model_modules([parent, child]))
        self.assertEqual(list(modules), ["project.py", "scope_unit.py"])
        with TemporaryDirectory() as folder:
            package = Path(folder) / "model_fixture"
            package.mkdir()
            (package / "__init__.py").write_text("")
            for filename, source in modules.items():
                (package / filename).write_text(source)
            with patch.object(sys, "path", [folder, *sys.path]):
                try:
                    project = importlib.import_module(
                        "model_fixture.project"
                    ).Project
                    scope_unit = importlib.import_module(
                        "model_fixture.scope_unit"
                    ).ScopeUnit
                    self.assertTrue(issubclass(project, scope_unit))
                    self.assertTrue(is_pydantic_dataclass(project))
                    self.assertEqual(
                        asdict(project("test")),
                        {"name": "test", "status": "Ready"},
                    )
                    with self.assertRaises(ValidationError):
                        project(123)
                    with self.assertRaises(ValidationError):
                        project("test", extra=True)
                    self.assertEqual(
                        __import__("typing").get_type_hints(project)["status"],
                        __import__("typing").Literal["Ready"],
                    )
                finally:
                    for key in list(sys.modules):
                        if key == "model_fixture" or key.startswith(
                            "model_fixture."
                        ):
                            del sys.modules[key]

    def test_module_annotation_dependencies_resolve(self):
        item = "from anechoic.model import Detail\n" + declaration(
            "Item"
        ).replace("    pass", "    detail: Detail")
        modules = assemble_model_modules([item, declaration("Detail")])
        self.assertIn("from .detail import Detail", modules["item.py"])
        cycle = "from anechoic.model import Item\n" + declaration(
            "Detail"
        ).replace("    pass", "    item: Item")
        with self.assertRaises(CycleError):
            assemble_model_modules([item, cycle])

    def test_nested_property_mapping_is_admitted_as_typed_model(self):
        imports = (
            "from anechoic.formal_claims import declare_entity\n"
            "from dataclasses import dataclass, field\n"
        )
        child = imports + (
            "@dataclass\nclass Child:\n    name: str\n"
            "declare_entity(entity_name='Child', entity_class=Child)\n"
        )
        parent = imports + (
            "from anechoic.model import Child\n@dataclass\nclass Parent:\n"
            "    child: Child = "
            "field(metadata={'property_occurrence_cardinality': 1, "
            "'dependent_property_cardinality': 1, 'value_cardinality': 0})\n"
            "declare_entity(entity_name='Parent', entity_class=Parent)\n"
        )
        module = ModuleType("nested_property_fixture")
        with patch.dict(sys.modules, {module.__name__: module}):
            exec(assemble_model_classes([child, parent]), vars(module))
            values = {"child": {"name": "valid"}}
            instance = validate_model_instance(
                module.Parent,
                properties=values,
                outgoing_relations={},
                relation_declarations={module.Parent: {}},
                model_types={},
                checks={},
                population_declarations={module.Parent: ()},
                population_peers={},
            )
            self.assertIsInstance(instance.child, module.Child)
            self.assertEqual(asdict(instance), values)
            self.assertTrue(
                is_dataclass(instance)
                and is_pydantic_dataclass(type(instance))
            )
            self.assertEqual(
                fields(module.Parent)[0].metadata[
                    "dependent_property_cardinality"
                ],
                1,
            )
            with self.assertRaises(ValidationError):
                module.Child(name=1)

    def test_missing_parent_and_cycle_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing Model parent"):
            assemble_model_classes([declaration("Project", "ScopeUnit")])
        with self.assertRaises(CycleError):
            assemble_model_classes(
                [declaration("A", "B"), declaration("B", "A")]
            )

    def test_invalid_inherited_dataclass_fields_fail_at_build(self):
        parent = declaration("Parent").replace(
            "    pass", "    optional: str = ''"
        )
        child = declaration("Child", "Parent").replace(
            "    pass", "    required: str"
        )
        with self.assertRaisesRegex(TypeError, "non-default argument"):
            assemble_model_classes([child, parent])

    def test_build_selects_current_model_declarations_before_assembly(self):
        def carrier(name, namespace, claim):
            return {
                "source": {"path": name + ".md", "atom_id": name},
                "read_view": {
                    "status": "active",
                    "content_role": "Requirement",
                },
                "subjects": {"governs": f"{namespace} <+ {name}"},
                "body": f"## Claim\n### Formal Claim\n```python\n{claim}```\n",
            }

        source = build_model_class_source(
            [
                carrier(
                    "Project",
                    "ANECHOIC_MODEL",
                    declaration("Project", "ScopeUnit"),
                ),
                carrier(
                    "ScopeUnit", "ANECHOIC_MODEL", declaration("ScopeUnit")
                ),
                carrier("Engine", "ANECHOIC_STRUCTURE", "invalid Python\n"),
            ]
        )
        namespace = {}
        exec(source, namespace)
        self.assertTrue(
            issubclass(namespace["Project"], namespace["ScopeUnit"])
        )

    def test_legacy_and_duplicate_declarations_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "native Python"):
            assemble_model_classes(["property_rule(address='A')"])
        with self.assertRaisesRegex(ValueError, "Duplicate Model class"):
            assemble_model_classes([declaration("A"), declaration("A")])


if __name__ == "__main__":
    unittest.main()
