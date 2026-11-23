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
  version: 15
  updated_at: 2026-10-29 07:17:28 +0400
---
## Summary

Validate the routing tree

# Summary

Validate the routing tree

## Scope

the ANECHOIC Routing Tree.

## Claim

the Evaluation of the ANECHOIC Routing Tree registered under CA-R-1640-PROJECT_CONFIGURATION-RULE--register-one-canonical-routing-tree **must** reject a routing tree **when** **any** of the following is present:

## Details

- an invalid schema;
- an unknown target;
- ambiguous precedence;
- a duplicate route identity;
- an authority effect that is **not** explicitly declared.
