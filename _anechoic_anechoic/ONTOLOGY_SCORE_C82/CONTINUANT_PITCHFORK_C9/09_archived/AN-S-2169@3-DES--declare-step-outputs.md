---
atom_family: SPEC
atom_id: AN-S-2169
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T23:01:36.136167+00:00"
---

## Summary

Declare Step.Outputs

## Claim

### Prose Claim

A Step declares its outputs when it produces values for subsequent Steps or the enclosing Workflow. A previous Step output is one permitted source of a binding.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(entity_name='Outputs', relation_name="IS_PROPERTY_OF", base_path='Atom/(.Header.Context.Role:=Operations)/Step')
```
