"""Native Relation declarations preserve the two endpoint cardinalities."""
from pathlib import Path
import sys, unittest
TOOL = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(TOOL.parent.parent), str(TOOL.parent), str(TOOL)]
from cfel_claim_constraints import extract_claim_constraints

class RelationCardinalityTests(unittest.TestCase):
    def test_preserves_endpoints_and_bounds(self):
        carrier = {
            'source': {'atom_id': 'CA-R-1', 'version': 1, 'path': 'fixture.md', 'sha256': 'a' * 64},
            'read_view': {'content_role': 'Requirement', 'type': 'Relation Declaration'},
            'body': """## Claim
### Formal Claim
```python
from caprmedio.formal_claims import Cardinality, declare_relation
declare_relation(
    relation_name="IS_CONTAINED_BY",
    source_endpoint={"level": "model_entities", "entity_paths": ("View",)},
    target_endpoint={"level": "model_entities", "entity_paths": ("Workspace",)},
    targets_per_source=1,
    sources_per_target=Cardinality(minimum=1, maximum=None),
)
```
""",
        }
        rows, diagnostics = extract_claim_constraints(carrier)
        self.assertEqual([], diagnostics)
        endpoints = {row['direction']: row for row in rows if row['kind'] == 'relation_endpoint'}
        self.assertEqual({'source', 'target'}, endpoints.keys())
        self.assertEqual(
            (('View',), ('Workspace',)),
            tuple(endpoints[direction]['endpoint']['entity_paths'] for direction in ('source', 'target')),
        )
        for endpoint in endpoints.values():
            self.assertEqual('IS_CONTAINED_BY', endpoint['relation'])
            self.assertEqual({'minimum': 1, 'maximum': 1}, endpoint['targets_per_source'])
            self.assertEqual({'minimum': 1, 'maximum': None}, endpoint['sources_per_target'])

if __name__ == '__main__': unittest.main()
