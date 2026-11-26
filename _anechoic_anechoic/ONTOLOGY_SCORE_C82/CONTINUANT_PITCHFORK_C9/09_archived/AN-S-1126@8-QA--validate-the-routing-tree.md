---
atom_family: SPEC
atom_id: AN-S-1126
container:
  component: C9
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Validate the routing tree

# Summary

Validate the routing tree

## Scope

the ANECHOIC Routing Tree.

## Claim

the Evaluation of the ANECHOIC Routing Tree registered under CA-R-1640-PROJECT_CONFIGURATION-CORE-REQUIREMENT--register-one-canonical-routing-tree **must** reject a routing tree **when** **any** of the following is present:

## Details

- an invalid schema;
- an unknown target;
- ambiguous precedence;
- a duplicate route identity;
- an authority effect that is **not** explicitly declared.
