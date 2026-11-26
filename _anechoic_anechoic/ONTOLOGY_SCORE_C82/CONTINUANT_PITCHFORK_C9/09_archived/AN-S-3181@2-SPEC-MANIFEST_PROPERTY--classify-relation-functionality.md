---
atom_family: SPEC
atom_id: AN-S-3181
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-24T16:58:01.499747+00:00'
---

## Summary

Classify Relation functionality

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation >| Functional

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
    classification = True
    allowed_values = ('yes', 'no')
```
