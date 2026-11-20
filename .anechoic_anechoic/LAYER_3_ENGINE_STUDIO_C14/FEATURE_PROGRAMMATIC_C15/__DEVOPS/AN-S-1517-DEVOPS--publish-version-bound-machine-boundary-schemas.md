---
atom_family: SPEC
atom_id: AN-S-1517
structure:
  container:
    component: C15
  tier: 5
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Publish version-bound machine boundary schemas

## Claim

### Prose Claim

External structured-data boundaries publish generated JSON Schema bound to delivered interface Revision, identifying owner/version, accepted fields/constraints/extras, serialization/version references and (if Pydantic) supported version boundary. Place it at component integration-contract location; do not select new versions/serialization or take component ownership.
