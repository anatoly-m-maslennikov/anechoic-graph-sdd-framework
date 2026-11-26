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
  version: 24
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Define Plan blocking

## Claim scope

Plan-blocking Relations in the Plan Graph.

## Claim

**in** the Plan Graph, `A BLOCKS B` **means** that Plan `B` may start only
after Plan `A` is Done. An inverse lookup is derived from the same explicit
fact and is not separately authored; Subject DEPENDS_ON remains distinct.

## Details

Plan endpoint admission, status, cardinality, authority and reachability belong
to the Plan Entity Definition CA-R-2511.
