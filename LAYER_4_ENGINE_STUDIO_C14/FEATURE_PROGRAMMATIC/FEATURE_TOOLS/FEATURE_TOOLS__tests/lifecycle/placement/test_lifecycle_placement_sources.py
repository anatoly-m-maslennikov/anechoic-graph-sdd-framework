"""The candidate compiler verifies the staged placement pins."""

from pathlib import Path
import json
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(TOOLS))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.FEATURE_TOOLS__tests__shared import (  # noqa: E402
    compile_candidate_schema,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ATOM_LIFECYCLE.sources.placement.placement_sources import (  # noqa: E402
    bootstrap_rows,
    inventory,
    pin,
    read_selected,
    validate_selection,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.FEATURE_TOOLS__tests.lifecycle.placement.test_lifecycle_formal_placement import (  # noqa: E402
    RULES,
    carrier,
    native_body,
    role_source,
)


class PlacementSourcesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "CA-R-1.md").write_text(
            carrier(
                "CA-R-1",
                "Requirement",
                "Active",
                "## Claim\n### Formal Claim\n```python\n"
                "from anechoic.formal_claims import declare_entity\n"
                "declare_entity(entity_name='Form', relation_name='IS_"
                "PROPERTY_OF', base_path='Atom.Header.Context', allowed_"
                "values=('Plan',))\n```\n",
                "ANECHOIC_MODEL <+ Atom.Header.Context.Form",
            )
        )
        role_source(self.root, "Concern", 77, "CA-R-77")
        role_source(self.root, "Plan", 3, "CA-R-78")
        self.delivery = self.root / "CA-D-1.md"
        self.delivery.write_text(
            carrier(
                "CA-D-1",
                "Delivery",
                "Active",
                native_body(RULES),
                "ANECHOIC_MODEL <+ Carrier",
            )
        )
        (self.root / "CA-D-2.md").write_text(
            carrier(
                "CA-D-2",
                "Delivery",
                "Active",
                "irrelevant",
                "ANECHOIC_MODEL <+ Other",
            )
        )
        self.manifest = self.root.parent / (self.root.name + "-selection.json")
        self.addCleanup(self.manifest.unlink, missing_ok=True)

    def test_selected_placement_compiles_like_bootstrap_inventory(self):
        selected = [pin(row) for row in bootstrap_rows(inventory(self.root))]
        self.manifest.write_text(json.dumps(selected))
        self.assertEqual(
            compile_candidate_schema(self.root),
            compile_candidate_schema(self.root, self.manifest),
        )

    def test_requirement_pins_check_role_subject_and_digest(self):
        (self.root / "CA-R-1.md").write_text(
            carrier(
                "CA-R-1", "Requirement", "Active", "body", "Atom.Header.Status"
            )
        )
        (self.root / "CA-R-2.md").write_text(
            carrier(
                "CA-R-2", "Requirement", "Active", "body", "Atom.Content.Other"
            )
        )
        selected = [pin(inventory(self.root, "R")[0])]
        self.assertEqual("CA-R-1.md", selected[0]["source_path"])
        self.assertEqual(64, len(selected[0]["sha256"]))
        pattern = re.compile(r"Atom\.Header\..*")
        self.assertEqual(
            "CA-R-1",
            read_selected(
                self.root,
                selected,
                role="Requirement",
                subject_pattern=pattern,
            )[0]["id"],
        )
        (self.root / "CA-R-1.md").write_text(
            (self.root / "CA-R-1.md").read_text() + "changed"
        )
        with self.assertRaises(ValueError):
            read_selected(
                self.root,
                selected,
                role="Requirement",
                subject_pattern=pattern,
            )

    def test_compiler_reads_selected_delivery_only(self):
        selected = [pin(row) for row in bootstrap_rows(inventory(self.root))]
        self.manifest.write_text(json.dumps(selected))
        real_read = Path.read_bytes
        read_paths = []

        def observed_read(path):
            read_paths.append(path)
            return real_read(path)

        with patch.object(Path, "read_bytes", observed_read):
            compile_candidate_schema(self.root, self.manifest)
        self.assertIn(self.delivery, read_paths)
        self.assertNotIn(self.root / "CA-D-2.md", read_paths)

    def test_selector_still_rejects_incomplete_selection(self):
        with self.assertRaisesRegex(ValueError, "all eligible"):
            validate_selection(inventory(self.root), [])

    def test_empty_selection_is_valid_for_minimal_model_without_placement(
        self,
    ):
        self.delivery.unlink()
        (self.root / "CA-R-77.md").unlink()
        (self.root / "CA-R-78.md").unlink()
        self.manifest.write_text("[]")
        self.assertNotIn(
            "placement",
            json.loads(compile_candidate_schema(self.root, self.manifest)),
        )

    def test_stale_missing_duplicate_and_unrelated_pins_fail(self):
        selected = [pin(row) for row in bootstrap_rows(inventory(self.root))]
        cases = [
            selected + selected,
            [{**selected[0], "sha256": "0" * 64}],
            [{**selected[0], "version": 2}],
            [{**selected[0], "id": "CA-D-2"}],
            [{**selected[0], "source_path": "../CA-D-1.md"}],
            [pin(row) for row in inventory(self.root)],
        ]
        for case in cases:
            with self.subTest(case=case):
                self.manifest.write_text(json.dumps(case))
                with self.assertRaises(ValueError):
                    compile_candidate_schema(self.root, self.manifest)
        self.manifest.write_text(json.dumps(selected))
        self.delivery.write_text(self.delivery.read_text() + "\nchanged\n")
        with self.assertRaises(ValueError):
            compile_candidate_schema(self.root, self.manifest)


if __name__ == "__main__":
    unittest.main()
