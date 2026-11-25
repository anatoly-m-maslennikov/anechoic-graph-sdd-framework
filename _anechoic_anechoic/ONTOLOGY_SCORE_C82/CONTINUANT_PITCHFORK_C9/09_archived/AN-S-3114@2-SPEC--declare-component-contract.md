---
atom_family: SPEC
atom_id: AN-S-3114
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-20T14:42:07.157939+00:00'
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

class ComponentContract(Contract):
    pass

declare_entity(
    entity_name='Component Contract',
    entity_class=ComponentContract,
    entity_kind='Primary',
)
```
