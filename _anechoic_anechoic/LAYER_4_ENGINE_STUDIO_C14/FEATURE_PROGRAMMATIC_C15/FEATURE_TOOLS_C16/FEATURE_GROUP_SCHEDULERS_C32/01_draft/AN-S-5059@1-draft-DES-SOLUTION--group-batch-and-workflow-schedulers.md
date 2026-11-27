---
atom_family: SPEC
atom_id: AN-S-5059
container:
  component: C32
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3070@4-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T11:22:36.001339+00:00'
---

## Summary

Group batch and workflow schedulers.

## Claim

### Prose Claim

Bind batch_scheduler to the C41 BATCH_SCHEDULER identity in AN-S-3074@4 and workflow_scheduler to the C42 WORKFLOW_SCHEDULER identity in AN-S-3075@4. AN-S-2814@1-draft proposes batch submission and result aggregation at C41 and step sequencing at C42. Neither child declares a callable entry point.

### Formal Claim

```python group
component_group(
    roles={'batch_scheduler': 'C41', 'workflow_scheduler': 'C42'},
    entry_points=(),
)
```
