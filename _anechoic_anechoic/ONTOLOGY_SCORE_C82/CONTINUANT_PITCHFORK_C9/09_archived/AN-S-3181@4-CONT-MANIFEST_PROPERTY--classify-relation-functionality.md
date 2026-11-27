---
atom_family: SPEC
atom_id: AN-S-3181
concern:
  subject: Functional
  path: Model/Graph/Relation
  relation: classifies
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T18:34:34.789837+00:00"
---

## Summary

Classify Relation functionality

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
    property.classification = True
    property.value.allowed = ('yes', 'no')
```
