---
atom_family: SPEC
atom_id: AN-S-3180
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.576593+00:00"
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

## References

AN-S-2697, AN-S-2674.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, Relation

class Transitive(Property):
    bearer = Relation
    property.classification = True
    property.value.allowed = ('yes', 'no')
```
