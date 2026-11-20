---
atom_family: SPEC
atom_id: AN-S-2674
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: '2026-11-13T22:48:44.142840+00:00'
---
## Summary

Derive Recursive Containment from Direct Containment

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="RECURSIVELY_CONTAINS",
    derived_from="CONTAINS",
    source_endpoint={"level": "model_entities_or_instances"},
    target_endpoint={"level": "model_entities_or_instances"},
)
```

## Semantics

The Host recursively contains the Target when one or more successive `CONTAINS` links lead from Host to Target. Intermediate Entities need only satisfy the endpoint constraints of `CONTAINS`. Derive this Relation from the existing links.
