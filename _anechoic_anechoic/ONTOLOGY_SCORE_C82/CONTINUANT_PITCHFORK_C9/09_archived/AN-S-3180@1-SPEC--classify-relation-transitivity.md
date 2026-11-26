---
atom_family: SPEC
atom_id: AN-S-3180
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-21T12:21:53Z'
---

## Summary

Classify Relation transitivity

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation >| Transitive

## Claim

### Prose Claim

Classify a Relation Type as Transitive when (A R B) and (B R C) imply
(A R C) within its declared endpoint domain. The value `yes` declares this
rule. The value `no` leaves composition to other explicit rules.

Keep derived links separate from authored direct facts.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Relation",
    allowed_classification_values={"Transitive": ("yes", "no")},
)
```

## References

AN-S-2697, AN-S-2636, AN-S-2674.
