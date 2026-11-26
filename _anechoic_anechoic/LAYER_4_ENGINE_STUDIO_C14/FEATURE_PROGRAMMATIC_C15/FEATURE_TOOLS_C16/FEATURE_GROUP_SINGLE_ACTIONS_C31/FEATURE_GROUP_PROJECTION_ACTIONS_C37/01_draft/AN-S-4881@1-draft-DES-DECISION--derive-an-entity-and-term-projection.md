---
atom_family: SPEC
atom_id: AN-S-4881
container:
  component: C37
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4880@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Derive an Entity and Term Projection.

## Claim

### Prose Claim

Resolve exactly one readable, non-escaping frontier before construction. Reject an absent or ambiguous frontier with a diagnostic and no Projection. For an admitted frontier, recognize source candidates separately from admission, retain supported facts and unknown regions, and bind source and derivation lineage. Return the non-authoritative result and applicable diagnostics without writing authority or a Projection Carrier.

The successful result is stable for identical bound inputs. Check graph and coverage conditions as described in AN-S-2524@19. A cycle or actual cardinality violation has a failed validation disposition. The Active Specs govern optional persistence; this read-only Solution does not model it. The Project Scope Unit graph is outside this Solution.

### Formal Claim

```python
component_workflow(
    component='C37', action='derive_entity_projection',
    machine={
        'id': 'c37_derive_entity_projection', 'initial': 'idle',
        'states': {
            'idle': {'on': {'request': {'target': 'resolving', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'resolving': {'on': {
                'valid_frontier': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'selected_frontier', 'outcome': 'captured'}}},
                'invalid_frontier': {'target': 'rejecting', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'frontier_error', 'outcome': 'returned'}}},
            }},
            'rejecting': {'on': {'reject': {'target': 'rejected', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'frontier_rejected'}}}}},
            'building': {'on': {'result': {'target': 'lineage', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'projection_result', 'outcome': 'returned'}}}}},
            'lineage': {'on': {'source_lineage': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'effect', 'target': 'source_lineage', 'outcome': 'returned'}}}}},
            'returning': {'on': {'return': {'target': 'returned', 'guard': {'type': 'matchesTrace', 'params': {'kind': 'output', 'outcome': 'projection_returned'}}}}},
            'returned': {'type': 'final'}, 'rejected': {'type': 'final'},
        },
    },
)
```

## Details

The trace checks only the named observable outcomes and forbidden writes. It does not prove frontier classification, graph content, lineage completeness, reproducibility or diagnostic accuracy. The prose and pinned Active Specs state those obligations.
