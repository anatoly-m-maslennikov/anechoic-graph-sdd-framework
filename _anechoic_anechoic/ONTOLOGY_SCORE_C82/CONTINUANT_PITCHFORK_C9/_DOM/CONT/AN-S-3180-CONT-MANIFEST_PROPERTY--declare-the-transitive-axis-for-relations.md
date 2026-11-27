---
atom_family: SPEC
atom_id: AN-S-3180
concern:
  subject: Transitive
  path: Model/Graph/Relation
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 6
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare the Transitive Axis for Relations

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
    property.axis = True
    property.value.allowed = ('yes', 'no')
```
