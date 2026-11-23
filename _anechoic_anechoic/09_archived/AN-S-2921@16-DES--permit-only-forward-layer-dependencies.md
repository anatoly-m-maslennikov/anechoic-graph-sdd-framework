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
  version: 16
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary
Permit only forward Layer dependencies

## Claim

**every** dependency between Project Layers **must** point from the Project root **or** an earlier Layer **to** a later Layer **in** the cumulative order.
