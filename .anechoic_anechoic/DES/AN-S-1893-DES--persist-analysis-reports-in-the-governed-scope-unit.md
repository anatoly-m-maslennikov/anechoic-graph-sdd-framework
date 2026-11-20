---
identity:
  atom_id: AN-S-1893
context:
  container:
    component: C00
  tier: 1
  lens: DES
state:
  status: active
  version: 17
  updated_at: '2026-11-11T18:56:17+04:00'
---
## Summary

Persist Analysis Reports in the governed Scope Unit

# Persist Analysis Reports in the governed Scope Unit

**when** an executable FPF analysis produces a persistent Project artifact, FPF **must** by default create a correctly formatted `CA-A` Analysis Report Carrier **in** the Analysis and Advisory Role folder derived under CA-D-296 in the narrowest resolved Scope Unit that **contains** the analyzed Claim Scope; routing-only work **must not** persist a report, an explicit non-persistent request **must** remain non-persistent, **and** unresolved identity, admission, topology, **or** placement **must** stop persistence rather than fall back **to** an ad hoc report Folder.
