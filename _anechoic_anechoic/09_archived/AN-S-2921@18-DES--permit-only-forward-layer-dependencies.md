---
atom_family: SPEC
atom_id: AN-S-2921
container:
  component: C00
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-11-11 16:42:09 +0400
---
## Summary
Permit only forward Layer dependencies

## Claim

### Prose Claim


**every** dependency between Project Layers **must** point from the Project root **or** an earlier Layer **to** a later Layer **in** the cumulative order.
