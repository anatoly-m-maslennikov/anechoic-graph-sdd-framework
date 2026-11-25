---
atom_family: SPEC
atom_id: AN-S-2674
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: '2026-11-13T08:13:26.277090+00:00'
---
## Summary

Derive Recursive Containment from Direct Containment

## Claim

### Formal Claim

```python
# model
relation(source='$container', name='RECURSIVELY_CONTAINS', target='$descendant')
classify(address='Relation//RECURSIVELY_CONTAINS', axis='Derivation', value='Derived', notation='relation')
```

## Semantics

The Host recursively contains the Target when one or more successive `CONTAINS` links lead from Host to Target. Intermediate Entities need only satisfy the endpoint constraints of `CONTAINS`. Derive this Relation from the existing links.
