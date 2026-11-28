---
atom_family: SPEC
atom_id: AN-S-5194
container:
  component: C59
tier: 0
context:
  template: solution
  lens: SPEC
relations:
  ANSWERS:
  - AN-S-3047@34
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-28T08:19:40.569840+00:00"
---

## Summary

Rebuild only the Realization Graph

## Claim

### Formal Claim

```python
component_workflow(component='C59', action='rebuild_only_realization_graph', machine={
    'id': 'c59_graph_rebuild',
    'initial': 'idle',
    'states': {
        'idle': {'on': {
            'enabled': {'to': 'building', 'expect': {
                'kind': 'trigger', 'target': 'C59.database_api',
                'detail': {'target': 'realization_graph', 'graph_enabled': True},
            }},
            'disabled': {'to': 'refusing', 'expect': {
                'kind': 'trigger', 'target': 'C59.database_api',
                'detail': {'target': 'realization_graph', 'graph_enabled': False},
            }},
        }},
        'building': {'on': {'publish': {'to': 'returning', 'expect': {
            'kind': 'effect', 'target': 'C59.graph_rebuild',
            'outcome': 'published', 'detail': {
                'graph_replaced': True, 'dependent_results_replaced': True,
                'independent_results_preserved': True,
                'atoms_preserved': True, 'structure_preserved': True,
            },
        }}}},
        'refusing': {'on': {'refuse': {'to': 'returning_refusal', 'expect': {
            'kind': 'effect', 'target': 'C59.graph_rebuild_reply',
            'outcome': 'refused', 'detail': {
                'message': 'Realization Graph is disabled',
            },
        }}}},
        'returning': {'on': {'reply': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'ready',
        }}}},
        'returning_refusal': {'on': {'reply': {'to': 'done', 'expect': {
            'kind': 'output', 'outcome': 'disabled',
        }}}},
        'done': {'type': 'final'},
    },
})
```

## Semantics

Prepare Graph facts from fresh source reads. Stage dependent result
replacements with the Graph transaction. Install the replacement result
IDs after commit while holding the owner lock.
