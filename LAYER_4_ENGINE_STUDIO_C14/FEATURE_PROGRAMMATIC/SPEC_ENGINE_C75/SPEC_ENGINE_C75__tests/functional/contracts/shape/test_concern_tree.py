import unittest

from .....render_concern_tree__pub import render_concern_tree


def carrier(path, subject, relation="is_contained_by", group="Current"):
    return {
        "source_path": subject,
        "status_group": group,
        "header_json": {
            "concern": {"path": path, "subject": subject, "relation": relation}
        },
    }


class ConcernTreeTests(unittest.TestCase):
    def test_reads_all_roots_and_selects_a_subtree(self):
        rows = [
            carrier("Definitions/Core", "Quality", "has_axis"),
            carrier("Definitions/Core >| Quality", "Reviewed"),
            carrier("Another.index", "Target", "affects"),
            carrier("Definitions/Core", "History", group="Archived"),
        ]
        lines = [
            "Another",
            "    index",
            "        Target",
            "Definitions",
            "    Core",
            "        Quality",
            "            Reviewed",
        ]
        self.assertEqual(lines, render_concern_tree(rows).splitlines())
        self.assertEqual(
            "Core\n    Quality\n        Reviewed",
            render_concern_tree(rows, "Definitions/Core"),
        )
        with self.assertRaisesRegex(ValueError, "Unknown Concern root"):
            render_concern_tree(rows, "Missing")

    def test_split_template_locator_keeps_its_readable_label(self):
        rows = [
            carrier(
                "Definitions/Atom//.Header.Context", "Template := test", "."
            )
        ]
        self.assertEqual(
            "Atom\n    (Header.Context.Template := test)",
            render_concern_tree(rows, "Definitions/Atom"),
        )

    def test_project_structure_uses_manifest_parents(self):
        structure = {
            "components": {
                "C1": {"parent": "C00", "fields": {"name": "Outer"}},
                "C2": {"parent": "C1", "fields": {"name": "Inner"}},
            },
            "packages": {
                "CS1": {"component": "C2", "fields": {}},
            },
        }
        rows = [carrier("Project Structure.components", "C2", "affects")]
        self.assertEqual(
            "Outer (C1)\n    Inner (C2)\n        CS1",
            render_concern_tree(
                rows, "Project Structure.components/C1", structure=structure
            ),
        )
