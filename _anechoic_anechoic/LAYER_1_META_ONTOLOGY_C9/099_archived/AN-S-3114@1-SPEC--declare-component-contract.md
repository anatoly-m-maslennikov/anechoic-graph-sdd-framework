---
atom_family: SPEC
atom_id: AN-S-3114
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Component Contract

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract//Component Contract

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Contract
from dataclasses import field

class ComponentContract(Contract):
    tier: int = field(metadata={"allowed_values": (1,)})

declare_entity(
    entity_name="Component Contract",
    entity_class=ComponentContract,
)
```
