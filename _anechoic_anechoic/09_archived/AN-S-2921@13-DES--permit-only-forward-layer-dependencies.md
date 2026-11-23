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
  version: 13
  updated_at: 2026-10-27 19:59:49 +0400
---
## Summary

Permit only forward Layer dependencies

# Permit only forward Layer dependencies

**every** dependency between Project Layers **must** point from the Project root **or** an earlier Layer **to** a later Layer **in** the cumulative order.
