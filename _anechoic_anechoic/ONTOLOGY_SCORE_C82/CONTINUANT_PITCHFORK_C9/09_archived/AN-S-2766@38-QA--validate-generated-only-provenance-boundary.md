---
atom_family: SPEC
atom_id: AN-S-2766
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 38
  updated_at: "2026-11-25T22:00:01.482356+00:00"
---
## Summary

Validate Generated-Only Provenance Boundary

## Claim

### Prose Claim


generated-only provenance validation.


generated-only provenance validation **must not** pass **if** an update **only** **to** generated Projections contributes an Implementation Relation **or** a generated Projection cites itself as its semantic input. the same boundary applies with **or** **without** a version-control integration.
