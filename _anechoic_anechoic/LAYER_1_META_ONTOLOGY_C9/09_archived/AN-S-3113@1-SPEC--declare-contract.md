---
atom_family: SPEC
atom_id: AN-S-3113
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare Contract

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import SpecAtom

class Contract(SpecAtom):
    guarantee: str
    tier: int | None = None

def check_contract(contract: Contract) -> bool:
    return bool(contract.guarantee.strip())

declare_entity(
    entity_name="Contract",
    entity_class=Contract,
    instance_relation_constraints={
        "CONTAINED_BY": {"target_entity_paths": ("Node//Artifact//Component",), "targets_per_source": 1},
    },
    instance_check=check_contract,
)
```
