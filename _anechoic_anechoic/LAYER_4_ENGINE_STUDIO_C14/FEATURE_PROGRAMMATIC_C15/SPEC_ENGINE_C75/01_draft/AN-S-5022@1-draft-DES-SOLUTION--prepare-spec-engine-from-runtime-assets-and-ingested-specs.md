---
atom_family: SPEC
atom_id: AN-S-5022
container:
  component: C75
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3395@3-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-26T22:00:52.285223+00:00'
---
## Summary

Prepare Spec Engine from runtime assets and ingested Specs

## Claim

### Prose Claim

Resolve the compiled Model through the existing admitted asset reader.
Use the image Model when the Project asset cannot be admitted, and report
that fallback. Ingestion stages the Project Spec rows in DuckDB before the
compiler consumes them. Use the same snapshot for Model, Structure, and
Formal Specification. Publish the resulting generation after validation.

### Formal Claim

```python
component_workflow(
    component='C75', action='prepare_spec_engine',
    machine={'id': 'prepare_spec_engine', 'initial': 'model', 'states': {
        'model': {'on': {
            'selected': {'to': 'sources', 'expect': {
                'kind': 'effect', 'target': 'C75.bootstrap_model', 'outcome': 'selected'}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'sources': {'on': {
            'snapshot': {'to': 'publish', 'expect': {
                'kind': 'effect', 'target': 'C95.source_snapshot', 'outcome': 'ready'}},
            'failed': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'failed'}},
        }},
        'publish': {'on': {'ready': {'to': 'done', 'expect': {'kind': 'output', 'outcome': 'ready'}}}},
        'done': {'type': 'final'},
    }},
)
```
