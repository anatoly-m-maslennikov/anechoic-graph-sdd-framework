"""Class assembly uses native Python inheritance without executing Claims."""

from dataclasses import asdict
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

from pydantic import ValidationError
from pydantic.dataclasses import is_pydantic_dataclass
from importlib.util import module_from_spec, spec_from_file_location
from unittest.mock import patch

from FEATURE_PROGRAMMATIC.FEATURE_FORMAL_MODEL_ENGINE import (
    native_model_lint__pub,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.assembly.model_class_assembly import (
    assemble_model_classes,
    build_model_class_source,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.FEATURE_FORMAL_MODEL_GENERATOR__shared import (
    select_model_declarations,
)
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_MODEL_VALIDATION.FEATURE_MODEL_VALIDATION__shared import (
    bind_model_declarations,
    validate_model_instance,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_MODEL_C51.\
    FEATURE_MODEL_VALIDATION.model_field_validation import (
    validate_model_fields,
)  # fmt: skip
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.model.claims.claims__shared import (
    parse_native_model_claim,
)


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


def _validator_rows():
    node_claim = (
        declaration("Node")
        .replace("    pass", "    identity: int")
        .replace(
            "entity_class=Node)",
            "entity_class=Node, "
            "population_unique_constraints=({'keys': ('Identity',)},))",
        )
    )
    property_claim = (
        "from anechoic.formal_claims import declare_entity\n"
        "declare_entity(entity_name='Identity', "
        "relation_name='IS_PROPERTY_OF', base_path='Node')\n"
    )
    relation_claim = (
        "from anechoic.formal_claims import declare_relation\n"
        "declare_relation(relation_name='IS_PROPERTY_OF', "
        "source_endpoint={'level': 'model_entities'}, "
        "target_endpoint={'level': 'model_entities'})\n"
    )

    def carrier(subject, claim):
        return {
            "source": {"path": subject + ".md", "atom_id": subject},
            "read_view": {
                "status": "active",
                "content_role": "Requirement",
            },
            "subjects": {"governs": "ANECHOIC_MODEL <+ " + subject},
            "body": f"## Claim\n### Formal Claim\n```python\n{claim}```\n",
        }

    rows = [
        carrier("Node", node_claim),
        carrier("Node.Identity", property_claim),
        carrier("Relation//IS_PROPERTY_OF", relation_claim),
    ]
    return rows


class ModelClassAssemblyMoreTests(unittest.TestCase):
    def test_plain_claim_class_becomes_dataclass(self):
        claim = (
            "from anechoic.formal_claims import declare_entity\n"
            "class Item:\n    name: str\n"
            "declare_entity(entity_name='Item', entity_class=Item)\n"
        )
        namespace = {}
        exec(assemble_model_classes([claim]), namespace)
        self.assertTrue(is_pydantic_dataclass(namespace["Item"]))
        self.assertEqual("hello", namespace["Item"]("hello").name)
        with self.assertRaises(ValidationError):
            namespace["Item"](123)

    def test_claim_dataclass_options_remain_effective(self):
        claim = declaration("Item").replace(
            "@dataclass", "@dataclass(frozen=True, slots=True, kw_only=True)"
        )
        claim = claim.replace("    pass", "    name: str = 'default'")
        namespace = {}
        exec(assemble_model_classes([claim]), namespace)
        item = namespace["Item"]()
        self.assertTrue(is_pydantic_dataclass(type(item)))
        self.assertEqual(asdict(item), {"name": "default"})
        with self.assertRaises(AttributeError):
            item.name = "changed"
        with self.assertRaises(ValidationError):
            namespace["Item"]("positional")

    def test_quoted_annotation_is_rejected_before_runtime_type_resolution(
        self,
    ):
        claim = declaration("Item").replace(
            "    pass", "    name: \"open('file', 'w')\""
        )
        with self.assertRaisesRegex(
            ValueError, "use an unquoted Python annotation"
        ):
            assemble_model_classes([claim])

    def test_string_literal_values_are_preserved_in_types(self):
        claim = "from typing import Literal\n" + declaration("Item").replace(
            "    pass", '    label: Literal["Ready"]'
        )
        self.assertIn("Literal['Ready']", assemble_model_classes([claim]))

    def test_field_cardinality_is_materialized_without_a_claim_helper_import(
        self,
    ):
        claim = (
            "from dataclasses import dataclass, field\n"
            "from anechoic.formal_claims import Cardinality, declare_entity\n"
            "@dataclass\nclass Item:\n"
            "    name: str = field(metadata={'values': "
            "Cardinality(minimum=1, maximum=1)})\n"
            "declare_entity(entity_name='Item', entity_class=Item)\n"
        )
        source = assemble_model_classes([claim])
        namespace = {}
        exec(source, namespace)
        self.assertNotIn("anechoic.formal_claims", source)
        field = namespace["Item"].__dataclass_fields__["name"]
        self.assertEqual(
            field.metadata["values"], {"minimum": 1, "maximum": 1}
        )

    def test_imported_class_validates_inherited_fields(self):
        claim = declaration("Base").replace("    pass", "    name: str")
        with TemporaryDirectory() as folder:
            path = Path(folder) / "model.py"
            path.write_text(
                assemble_model_classes([declaration("Child", "Base"), claim])
            )
            spec = spec_from_file_location("test_generated_model", path)
            module = module_from_spec(spec)
            with patch.dict(sys.modules, {spec.name: module}):
                spec.loader.exec_module(module)
                validate_model_fields(module.Child, {"name": "valid"})
                with self.assertRaises(ValueError):
                    validate_model_fields(module.Child, {"name": 1})

    def test_selected_declarations_drive_the_shared_validator(self):
        rows = _validator_rows()
        namespace = {}
        exec(build_model_class_source(rows), namespace)
        declarations = [
            (subject, parse_native_model_claim(claim))
            for _, subject, claim in select_model_declarations(rows)
        ]
        relations, model_types, populations = bind_model_declarations(
            declarations, namespace
        )
        node = namespace["Node"]
        args = {
            "properties": {"identity": 1},
            "outgoing_relations": {},
            "checks": {},
            "relation_declarations": relations,
            "model_types": model_types,
            "population_declarations": populations,
        }
        self.assertEqual(
            validate_model_instance(node, population_peers={node: []}, **args),
            node(1),
        )
        with self.assertRaisesRegex(
            ValueError, "Population uniqueness violated"
        ):
            validate_model_instance(
                node, population_peers={node: [node(1)]}, **args
            )

    def test_selected_declarations_share_one_address_catalog_per_run(self):
        rows = _validator_rows()
        with patch.object(
            native_model_lint__pub,
            "_catalog",
            wraps=native_model_lint__pub._catalog,
        ) as catalog:
            self.assertEqual(len(select_model_declarations(rows)), len(rows))
            catalog.assert_called_once()
            with self.assertRaisesRegex(
                ValueError,
                "unknown population Property address: Node.Identity",
            ):
                select_model_declarations([rows[0], rows[2]])
            self.assertEqual(catalog.call_count, 2)


if __name__ == "__main__":
    unittest.main()
