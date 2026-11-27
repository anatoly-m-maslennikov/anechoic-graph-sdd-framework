import unittest

from ..model_entity_tree import model_tree_rows


class ModelTreeTests(unittest.TestCase):
    def test_placements_and_selectors_come_from_the_accepted_descriptor(self):
        entities = [
            (path, path, {"entity_name": name})
            for path, name in (
                ("Schema", "Schema"),
                ("Branch", "Branch"),
                ("Branch//Variant", "Variant"),
                ("Branch//Variant/Child", "Child"),
            )
        ]
        locations = {
            "Branch": ("Schema", "/", "Branch"),
            "Branch//Variant": ("Branch", "//", "(Options.Mode := example)"),
        }
        rows = model_tree_rows(entities, locations, lambda path: path)
        by_path = {row[0]: row for row in rows}
        self.assertEqual(
            ("Schema/Branch", "Branch", "Schema", "/"), by_path["Branch"][1:]
        )
        self.assertEqual(
            (
                "Schema/Branch//(Options.Mode := example)/Child",
                "Child",
                "Branch//Variant",
                "/",
            ),
            by_path["Branch//Variant/Child"][1:],
        )
        self.assertEqual(len(entities), len(rows))
