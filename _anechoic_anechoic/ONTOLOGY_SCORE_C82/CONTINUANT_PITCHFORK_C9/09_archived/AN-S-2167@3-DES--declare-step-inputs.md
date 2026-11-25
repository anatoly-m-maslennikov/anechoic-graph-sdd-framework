---
atom_family: SPEC
atom_id: AN-S-2167
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:01:35.682805+00:00"
---

## Summary

Declare Step.Inputs

## Claim

### Prose Claim

Step Inputs are optional. They identify the input values used by the Step; bindings supply values.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(entity_name='Inputs', relation_name="IS_PROPERTY_OF", base_path='Atom/(.Header.Context.Role:=Operations)/Step')
```
