---
atom_family: SPEC
atom_id: AN-S-4892
container:
  component: C32
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3070
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T11:30:16.603936+00:00'
---

## Summary

Group batch and workflow schedulers

## Guarantee

Keep Batch Scheduler and Workflow Scheduler as distinct child Components.

## Claim

### Formal Claim

```python group
declare_group_contract(
    roles={'batch_scheduler': 'C41', 'workflow_scheduler': 'C42'},
)
```
