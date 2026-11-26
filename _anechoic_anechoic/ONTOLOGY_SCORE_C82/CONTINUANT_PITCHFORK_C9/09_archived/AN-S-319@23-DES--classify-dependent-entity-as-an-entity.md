---
atom_family: SPEC
atom_id: AN-S-319
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 23
  updated_at: "2026-11-25T22:50:38.523756+00:00"
---
## Summary

Classify Dependent Entity as an Entity

## Claim scope

the `Entity/Dependent Entity` kind and its relation to Entity.

## Claim

`Entity/Dependent Entity` **must** be NARROWER_THAN `Entity`.

## Details

`Entity/Dependent Entity` names an Entity kind; its `/` path expresses
specialization. `Entity/Term//Dependent Entity` names the reusable lexical
Term used to write that kind and other qualified entity names. The Term is not
the kind, and mentioning or parsing the Term does not introduce an Entity
occurrence.

An `Entity/Dependent Entity` occurrence has an immediate bearer identified by
an outgoing direct IS_BORNE_BY Relation to that bearer. This Rule classifies
the kind; the Relation Definition supplies relation meaning and the separate
bearer-cardinality Rule supplies the occurrence constraint.

### Withdrawn preparation — Property consolidation

The Property kind is defined directly under Entity by R1193's successor. This former separate Dependent Entity classification preparation is redundant after the Operator's consolidation decision. Current R1267 remains unchanged until an explicitly governed adoption disposition. The prior preparation is retained as historical review evidence. Do not promote this Draft as written or treat this marker as Current-source retirement.
