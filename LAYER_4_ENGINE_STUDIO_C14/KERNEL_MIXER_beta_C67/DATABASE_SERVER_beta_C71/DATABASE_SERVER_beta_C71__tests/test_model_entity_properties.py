import unittest

from ..model_entity_properties import primary_entity_properties


def _properties():
    def prop(name, base, **args):
        return (
            None,
            {
                "entity_kind": "Property",
                "entity_name": name,
                "base_path": base,
                **args,
            },
        )

    return [
        prop("Header", "Base", value_cardinality=0),
        prop(
            "Template",
            "Base.Header",
            value_cardinality=1,
            allowed_values=["A", "B"],
            field_options={"default": "A"},
        ),
        prop(
            "Template",
            "Base.Header",
            applies_to_entity_classes=["Child"],
            allowed_values=["B"],
        ),
        prop("Items", "Base", field_options={"default_factory": "list"}),
    ]


class EffectivePropertiesTest(unittest.TestCase):
    def test_inheritance_refinement_groups_and_defaults(self):
        entities = [
            (None, path, {"entity_class": name})
            for name, path in (
                ("Base", "Base"),
                ("Child", "Base//Child"),
                ("Grandchild", "Base//Child//Grandchild"),
                ("Contained", "Base/Contained"),
            )
        ]
        properties = _properties()
        aliases = {"Child": "Base//Child"}
        result = primary_entity_properties(
            entities,
            properties,
            {"Child": ("Base",), "Grandchild": ("Child",)},
            lambda path: aliases.get(path, path),
        )
        self.assertEqual([], result["Base/Contained"])
        self.assertEqual(
            ["Header", "Header.Template", "Items"],
            [item["property_path"] for item in result["Base"]],
        )
        base, child, grandchild = [
            result[path][1]
            for path in ("Base", "Base//Child", "Base//Child//Grandchild")
        ]
        self.assertEqual("A", base["default_value"])
        self.assertNotIn("fixed_value", base)
        self.assertEqual("B", child["fixed_value"])
        self.assertEqual("Base//Child", grandchild["declared_on"])
        self.assertFalse(child["inherited"])
        self.assertTrue(grandchild["inherited"])
        self.assertEqual("list", result["Base"][2]["default_factory"])

    def test_accepted_legacy_property_without_entity_kind(self):
        properties = [
            (
                None,
                {
                    "relation_name": "IS_PROPERTY_OF",
                    "entity_name": "Action",
                    "base_path": "Event Record",
                    "value_format": "str",
                },
            )
        ]
        entities = [(None, "Event Record", {"entity_class": "EventRecord"})]
        (fields,) = primary_entity_properties(
            entities, properties, {}, lambda path: path
        )["Event Record"]
        self.assertEqual("Action", fields["property_path"])
        self.assertFalse(fields["inherited"])


if __name__ == "__main__":
    unittest.main()
