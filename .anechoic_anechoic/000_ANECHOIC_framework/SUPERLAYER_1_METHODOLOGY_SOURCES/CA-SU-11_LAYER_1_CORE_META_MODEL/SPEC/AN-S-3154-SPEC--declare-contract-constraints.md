---
atom_family: SPEC
atom_id: AN-S-3154
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T14:42:07.157939+00:00'
---

## Summary

Declare Contract Constraints

## Claim scope

MODEL//ANECHOIC <+ Node//Artifact//Atom//Spec Atom//Contract.Constraints

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Contract

def check_contract(contract: Contract) -> bool:
    return bool(contract.guarantee.strip())

declare_entity(
    entity_name='Contract Constraints',
    constraints_for='Node//Artifact//Atom//Spec Atom//Contract',
    instance_relation_constraints={'CONTAINED_BY': {'target_entity_paths': ('Node//Artifact//Component',), 'targets_per_source': 1}},
    instance_check=check_contract,
)
```
