"""Native Relation declarations preserve the two endpoint cardinalities."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(TOOL := Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(TOOL.parent))
sys.path.insert(0, str(TOOL.parent.parent))
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.claims.\
    claims__shared import (
    extract_claim_constraints,
)  # fmt: skip


def _relation_carrier():
    carrier = {
        "source": {
            "atom_id": "CA-R-1",
            "version": 1,
            "path": "fixture.md",
            "sha256": "a" * 64,
        },
        "read_view": {
            "content_role": "Requirement",
            "type": "Relation Declaration",
        },
        "body": (
            "## Claim\n"
            "### Formal Claim\n"
            "```python\n"
            "from anechoic.formal_claims import Cardinality, declare_"
            "relation\n"
            "declare_relation(\n"
            '    relation_name="IS_CONTAINED_BY",\n'
            '    source_endpoint={"level": "model_entities", "entity_'
            'paths": ("View",)},\n'
            '    target_endpoint={"level": "model_entities", "entity_'
            'paths": ("Workspace",)},\n'
            "    targets_per_source=1,\n"
            "    sources_per_target=Cardinality(minimum=1, maximum=No"
            "ne),\n"
            ")\n"
            "```\n"
        ),
    }
    return carrier


class RelationCardinalityTests(unittest.TestCase):
    def test_preserves_endpoints_and_bounds(self):
        carrier = _relation_carrier()
        rows, diagnostics = extract_claim_constraints(carrier)
        self.assertEqual([], diagnostics)
        endpoints = {
            row["direction"]: row
            for row in rows
            if row["kind"] == "relation_endpoint"
        }
        self.assertEqual({"source", "target"}, endpoints.keys())
        self.assertEqual(
            (("View",), ("Workspace",)),
            tuple(
                endpoints[direction]["endpoint"]["entity_paths"]
                for direction in ("source", "target")
            ),
        )
        for endpoint in endpoints.values():
            self.assertEqual("IS_CONTAINED_BY", endpoint["relation"])
            self.assertEqual(
                {"minimum": 1, "maximum": 1}, endpoint["targets_per_source"]
            )
            self.assertEqual(
                {"minimum": 1, "maximum": None}, endpoint["sources_per_target"]
            )


if __name__ == "__main__":
    unittest.main()
