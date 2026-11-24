---
atom_family: SPEC
atom_id: AN-S-4740
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: active
  version: 1
  updated_at: '2026-11-23T18:03:30.250723+00:00'
relations:
  IS_REFERENCE:
  - AN-S-4735
  - AN-S-3310
  - AN-S-1342
---

## Summary

Check source ownership and boundaries

## Claim

### Prose Claim

#### Ownership and boundaries

Check source ownership and imports against the declared code boundaries.
Check declared state boundaries and Python child import boundaries. Check
Python launchers for bytecode containment and the independent launch roots
required by AN-S-3310. Apply AN-S-1342 to temporary and cache placement.
