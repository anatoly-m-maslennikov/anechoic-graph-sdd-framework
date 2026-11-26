---
atom_family: SPEC
atom_id: AN-S-4893
container:
  component: C32
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4892@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T11:30:16.603936+00:00'
---

## Summary

Group batch and workflow schedulers

## Claim

### Prose Claim

Bind the batch and workflow roles to C41 and C42. General scheduling inputs, results, and failure rules remain open.

### Formal Claim

```python group
component_group(
    roles={'batch_scheduler': 'C41', 'workflow_scheduler': 'C42'},
)
```
