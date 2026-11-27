"Explicit Aspect membership in Python retains the complete written identity."

from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent), str(TOOL)]

from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import (  # noqa: E402
    compose_enhanced_current_graph,
)
from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.GENERATE_ENTITY_GRAPH.GENERATE_ENTITY_GRAPH__shared import (  # noqa: E402
    render_model,
)


def carrier(atom_id, subject, address):
    name = address.rsplit(" <+ ", 1)[-1]
    return {
        "source": {
            "atom_id": atom_id,
            "version": 1,
            "path": f"{atom_id}.md",
            "sha256": "a" * 64,
        },
        "subjects": {}
        if subject is None
        else {"active": subject, "passive": []},
        "body": (
            "## Claim\n### Formal Claim\n```python\n"
            "from anechoic.formal_claims import declare_entity\n"
            "from anechoic.model import Aspect\n"
            f"declare_entity(entity_name={name!r}, instance=Aspect(address={address!r}))\n"
            "```\n"
        ),
        "read_view": {"content_role": "Requirement", "type": "Declaration"},
    }


def instance_edges(graph):
    identities = {node["id"]: node["identity"] for node in graph["nodes"]}
    return {
        (
            identities[edge["relation_source"]],
            identities[edge["relation_target"]],
        )
        for edge in graph["edges"]
        if edge["kind"] == "INSTANCE_OF"
    }


class AspectClaimProjectionTests(unittest.TestCase):
    def test_grouped_formal_claim_preserves_full_identity_without_subject_fallback(
        self,
    ):
        first = (
            "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ "
            "Operation <+ Data Handling <+ Query Processing"
        )
        second = (
            "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Other <+ Query "
            "Processing"
        )
        graph, provenance = compose_enhanced_current_graph(
            [
                carrier("CA-R-1", "Unrelated Main Subject", first),
                carrier("CA-R-2", None, second),
            ]
        )
        edges = instance_edges(graph)
        self.assertIn((first, "Aspect"), edges)
        self.assertIn((second, "Aspect"), edges)
        self.assertNotIn(("Query Processing", "Aspect"), edges)
        self.assertNotIn(("Unrelated Main Subject", "Aspect"), edges)
        self.assertTrue(
            any(
                row.get("role") == "formal_claim"
                for row in provenance["occurrences"]
            )
        )
        rendered = render_model(
            graph,
            provenance,
            updated_at="2026-11-11 00:00:00 +0000",
            source_selection="Fixture",
            projection_identity={
                "projection_id": "CA-PROJ-901",
                "named_selection": "Current Atoms",
            },
        )
        self.assertIn(f"`INSTANCE_OF` `{first}` → `Aspect`", rendered)
        self.assertIn(f"`INSTANCE_OF` `{second}` → `Aspect`", rendered)

    def test_typed_aspects_with_same_name_keep_distinct_paths(self):
        paths = [
            "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ "
            + parent
            + " <+ Example"
            for parent in ("Engineering", "Product")
        ]
        rows = [
            carrier(f"CA-R-{index}", path, path)
            for index, path in enumerate(paths)
        ]
        graph, _ = compose_enhanced_current_graph(rows)
        self.assertTrue(
            {(path, "Aspect") for path in paths} <= instance_edges(graph)
        )

    def test_ordinary_claim_does_not_declare_aspect_membership(self):
        path = "PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Example"
        row = carrier("CA-R-3", None, path)
        row["read_view"]["type"] = "Requirement"
        graph, _ = compose_enhanced_current_graph([row])
        self.assertNotIn((path, "Aspect"), instance_edges(graph))


if __name__ == "__main__":
    unittest.main()
