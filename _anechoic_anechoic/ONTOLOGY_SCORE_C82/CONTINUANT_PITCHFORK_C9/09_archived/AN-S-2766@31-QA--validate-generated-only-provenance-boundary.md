---
atom_family: SPEC
atom_id: AN-S-2766
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 31
  updated_at: 2026-10-27 19:59:38 +0400
---
## Summary

Validate Generated-Only Provenance Boundary

# Summary

Validate Generated-Only Provenance Boundary

## Scope

generated-only provenance validation.

## Claim

generated-only provenance validation **must not** pass **if** an update **only** **to** generated Projections contributes an Implementation Relation **or** a generated Projection cites itself as its semantic input. the same boundary applies with **or** **without** a version-control integration.

## Details
