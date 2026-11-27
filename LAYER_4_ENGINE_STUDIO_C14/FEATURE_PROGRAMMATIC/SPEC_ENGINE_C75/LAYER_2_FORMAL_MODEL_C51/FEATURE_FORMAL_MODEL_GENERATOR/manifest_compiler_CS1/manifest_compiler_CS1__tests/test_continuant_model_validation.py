import tempfile
import unittest
from pathlib import Path

# fmt: off
from FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.\
    LAYER_2_FORMAL_MODEL_C51.FEATURE_FORMAL_MODEL_GENERATOR.\
    manifest_compiler_CS1 import (
    active_model_sources as sources,
)
# fmt: on


def _continuant_text(ident, subject, parent, relation, body):
    return f"""---
atom_family: SPEC
atom_id: AN-S-{ident}
concern:
  subject: {subject}
  path: {parent}
  relation: {relation}
container:
  component: C9
tier: 2
context:
  lens: DOM/CONT
  template: manifest_node
state:
  status: active
  version: 1
  updated_at: 2026-11-20T00:00:00Z
---
## Formal Manifest

```python anechoic-edsl
{body}
```
"""


class ContinuantModelSourceTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp_path = Path(directory.name)

    def test_continuant_field_concern_matches_formal_address(self):
        check = sources._check_continuant_address
        source = "META_ONTOLOGY_C9/_DOM/CONT/AN-S-1-CONT--field.md@1"
        prop = (
            "from anechoic.formal_claims import declare_entity\n"
            "declare_entity(entity_name='Tier', entity_kind='Property', "
            "relation_name='IS_PROPERTY_OF', "
            "base_path='Graph/Node//Spec.Header', "
            "value_format=int, "
            "applies_to_entity_classes=('Graph/Node//Project',))\n"
        )
        text = "class Tier(Property):\n    pass\n"
        check(
            source,
            "MODEL//ANECHOIC <+ Graph/Node//Project.Header.Tier",
            text,
            "manifest_property",
            {},
            prop,
        )
        with self.assertRaisesRegex(ValueError, "does not match"):
            check(
                source,
                "MODEL//ANECHOIC <+ Graph/Node//Project.Header.Other",
                text,
                "manifest_property",
                {},
                prop,
            )
        self._check_relation_concern(check, source)

    def _check_relation_concern(self, check, source):
        relation = (
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='CALLS', "
            "source_endpoint={'level': 'model_entities'}, "
            "target_endpoint={'level': 'model_entities'})\n"
        )
        text = "class Calls(Relation):\n    pass\n"
        check(
            source,
            "MODEL//ANECHOIC <+ Graph/Relation//CALLS",
            text,
            "manifest_relation",
            {"Relation": "Graph/Relation"},
            relation,
        )
        with self.assertRaisesRegex(ValueError, "does not match"):
            check(
                source,
                "MODEL//ANECHOIC <+ Graph/Relation//OTHER",
                text,
                "manifest_relation",
                {"Relation": "Graph/Relation"},
                relation,
            )

    def test_continuant_parent_validation_runs_on_ingested_rows(self):
        # fmt: off
        from FEATURE_PROGRAMMATIC.FEATURE_TOOLS.ADAPTERS_C30.\
            carrier_read__pub import parse_carrier
        # fmt: on

        folder = self.tmp_path / "META_ONTOLOGY_C9" / "_DOM" / "CONT"
        folder.mkdir(parents=True)
        rows = []
        for ident, subject, parent, relation, body in (
            (1, "Graph", "Model", "is_contained_by", "class Graph:\n    pass"),
            (
                2,
                "Parent",
                "Model/Graph",
                "is_narrower_than",
                "from anechoic.model import Graph\n"
                "class Parent(Graph):\n    pass",
            ),
            (
                3,
                "Child",
                "Model/Graph//Parent",
                "is_narrower_than",
                "from anechoic.model import Graph\n"
                "class Child(Graph):\n    pass",
            ),
        ):
            text = _continuant_text(ident, subject, parent, relation, body)
            path = folder / f"AN-S-{ident}-CONT--node.md"
            carrier = parse_carrier(text.encode(), path)
            rows.append(
                {
                    "source_path": str(path.relative_to(self.tmp_path)),
                    "exact_ref": f"AN-S-{ident}@1",
                    "metadata": carrier.metadata,
                    "body": carrier.body,
                }
            )
        with self.assertRaisesRegex(ValueError, "direct node base"):
            sources.compile_active_model_rows(rows, has_c9=True)

    def test_continuant_containment_requires_explicit_pair(self):
        relation = (
            "from anechoic.formal_claims import declare_relation\n"
            "declare_relation(relation_name='IS_CONTAINED_BY', "
            "endpoint_pairs=("
            "{'source_endpoint': {'level': 'model_entities', "
            "'entity_paths': ('Graph/Node',)}, "
            "'target_endpoint': {'level': 'model_entities', "
            "'entity_paths': ('Graph',)}},))\n"
        )
        records = [
            (
                "relation",
                "MODEL//ANECHOIC <+ Graph/Relation//IS_CONTAINED_BY",
                relation,
            )
        ]
        source = "META_ONTOLOGY_C9/_DOM/CONT/AN-S-1-CONT--node.md@1"

        def node(scope):
            return (
                source,
                "MODEL//ANECHOIC <+ " + scope,
                "class Node:\n    pass\n",
                "manifest_node",
            )

        sources._check_continuant_containment(
            records, [node("Graph/Node"), node("Model")]
        )
        sources._check_continuant_containment([], [node("Graph/Other")])
        with self.assertRaisesRegex(ValueError, "absent from IS_CONTAINED_BY"):
            sources._check_continuant_containment(
                records, [node("Graph/Other")]
            )


if __name__ == "__main__":
    unittest.main()
