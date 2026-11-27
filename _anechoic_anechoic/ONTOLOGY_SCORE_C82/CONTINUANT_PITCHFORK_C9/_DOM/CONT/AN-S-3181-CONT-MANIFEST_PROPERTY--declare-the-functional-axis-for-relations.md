---
atom_family: SPEC
atom_id: AN-S-3181
concern:
  subject: Functional
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
  version: 5
  updated_at: '2026-11-26T18:34:31.644797+00:00'
---

## Summary

Declare the Functional Axis for Relations

## Claim

### Prose Claim

Classify a Relation Type as Functional when each source has at most one
distinct target within its declared endpoint domain. The value `yes` sets
the maximum number of targets per source to one. Any minimum comes from
the applicable cardinality constraint. The value `no` leaves the maximum
to other explicit constraints.

## References

AN-S-2697, AN-S-2789.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Property, Relation

class Functional(Property):
    bearer = Relation
    property.axis = True
    property.value.allowed = ('yes', 'no')
```
