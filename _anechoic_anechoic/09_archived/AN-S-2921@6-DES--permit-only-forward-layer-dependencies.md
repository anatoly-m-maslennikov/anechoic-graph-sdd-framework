---
atom_family: SPEC
atom_id: AN-S-2921
container:
  component: C00
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 01:33:47 +0400
---
## Summary

Permit only forward Layer dependencies

# Permit only forward Layer dependencies

**every** dependency between Project Layers **must** point from the Project root **or** an earlier Layer **to** a later Layer **in** the cumulative order.
