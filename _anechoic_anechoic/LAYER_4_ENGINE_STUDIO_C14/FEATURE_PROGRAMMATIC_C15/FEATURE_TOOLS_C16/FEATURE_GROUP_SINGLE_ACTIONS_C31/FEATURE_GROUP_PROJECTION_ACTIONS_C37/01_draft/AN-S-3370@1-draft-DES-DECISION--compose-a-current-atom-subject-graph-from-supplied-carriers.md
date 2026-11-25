---
atom_family: SPEC
atom_id: AN-S-3370
container:
  component: C37
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-22T23:43:31.971878+00:00'
---

## Summary

Compose a current Atom subject graph from supplied carriers

## Claim

### Prose Claim

From supplied current carriers, collect subject occurrences and build
sorted graph nodes, edges and provenance. An unsupported path raises unless
diagnostic mode is selected.

### Formal Claim

```python
component_workflow(
    component='C37',
    action='compose_current_atom_subject_graph',
    machine={
        'id': 'c37_compose_current_atom_subject_graph',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'carriers_supplied': {'target': 'composing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'composing': {'on': {
                'graph_and_provenance_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'unsupported_path_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Draft models one bounded workflow. Event names describe the expected
trace for review.

A Tier 0 Contract for this workflow is missing.
