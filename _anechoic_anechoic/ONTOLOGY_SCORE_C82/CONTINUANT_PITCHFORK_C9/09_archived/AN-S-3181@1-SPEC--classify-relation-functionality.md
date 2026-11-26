---
atom_family: SPEC
atom_id: AN-S-3181
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

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Relation",
    allowed_classification_values={"Functional": ("yes", "no")},
)
```

## References

AN-S-2697, AN-S-2789.
