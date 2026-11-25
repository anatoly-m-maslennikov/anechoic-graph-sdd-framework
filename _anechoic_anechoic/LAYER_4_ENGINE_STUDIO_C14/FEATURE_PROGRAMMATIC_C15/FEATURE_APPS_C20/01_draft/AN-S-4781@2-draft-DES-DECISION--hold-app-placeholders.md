---
atom_family: SPEC
atom_id: AN-S-4781
container:
  component: C20
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4780@2-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T11:11:23.887958+00:00'
---

## Summary

Hold App placeholders

## Claim

### Prose Claim

The placeholder leaves Apps available for future realizations. Its current grouping has no executable entry point.

### Formal Claim

```python group
component_group(
    roles={},
    entry_points=(),
)
```
