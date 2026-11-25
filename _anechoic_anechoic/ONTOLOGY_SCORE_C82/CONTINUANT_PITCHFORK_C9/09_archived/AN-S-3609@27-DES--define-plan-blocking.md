---
atom_family: SPEC
atom_id: AN-S-3609
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 27
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Define Plan blocking

## Claim

### Formal Claim

```CFEL
# model
Relation//BLOCKS ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Plan//$plan ((BLOCKS)) Plan//$plan_2;
```

### Prose Claim

#### Applicability
Plan-blocking Relations in the Plan Graph.

**in** the Plan Graph, `A BLOCKS B` **means** that Plan `B` may start only
after Plan `A` is Done. An inverse lookup is derived from the same explicit
fact and is not separately authored; Subject DEPENDS_ON remains distinct.

Forward `Host ((BLOCKS)) Target` and reverse `Target <((BLOCKS)) Host` are views of the same Relation fact.
BLOCKS relates prerequisite Plan to dependent Plan.

#### Details
Plan endpoint admission, status, cardinality, authority and reachability belong
to the Plan Entity Definition CA-R-2511.
