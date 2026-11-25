---
atom_family: SPEC
atom_id: AN-S-4996
container:
  component: C36
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3081
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:42:19.547178+00:00'
---

## Summary

Reserve SCOPE_UNIT_ACTIONS

## Guarantee

This Draft reserves SCOPE_UNIT_ACTIONS as C36 without contributing a callable entry point. A separate callable boundary requires admission. It makes no claim about current runtime behavior.

## Claim

### Formal Claim

```python group
declare_group_contract(
    roles={},
    entry_points=(),
)
```
