---
atom_family: SPEC
atom_id: AN-S-292
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 06:47:02 +0400
---
## Summary

Materialize FPF from a pinned base and ordered overlay

# Materialize FPF from a pinned base and ordered overlay

**every** FPF Extension Candidate **must** be materialized reproducibly from **`=1`** exact upstream FPF source revision **and** **`=1`** ordered project-owned patch overlay, **and** its immutable manifest **must** identify the complete base inventory **and** digest, **every** ordered overlay input **and** digest, the resulting inventory **and** digest, the exact Extension version, the intended behavior changes, preserved upstream behavior, affected paths, **and** acceptance Evaluations.
