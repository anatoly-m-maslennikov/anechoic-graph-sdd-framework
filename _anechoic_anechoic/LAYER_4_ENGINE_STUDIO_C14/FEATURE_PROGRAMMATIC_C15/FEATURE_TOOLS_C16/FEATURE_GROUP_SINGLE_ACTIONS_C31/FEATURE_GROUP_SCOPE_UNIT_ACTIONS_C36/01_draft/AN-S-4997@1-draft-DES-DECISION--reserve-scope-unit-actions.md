---
atom_family: SPEC
atom_id: AN-S-4997
container:
  component: C36
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4996@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:42:19.547178+00:00'
---

## Summary

Reserve SCOPE_UNIT_ACTIONS

## Claim

### Prose Claim

This Draft reserves SCOPE_UNIT_ACTIONS as C36 without contributing a callable entry point. A separate callable boundary requires admission. It makes no claim about current runtime behavior.

### Formal Claim

```python group
component_group(
    roles={},
    entry_points=(),
)
```
