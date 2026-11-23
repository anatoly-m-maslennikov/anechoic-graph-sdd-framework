---
atom_family: SPEC
atom_id: AN-S-1893
container:
  component: C00
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 20:51:15 +0400
---
## Summary

Persist Analysis Reports in the governed Scope Unit

# Persist Analysis Reports in the governed Scope Unit

**when** an executable FPF analysis produces a persistent Project artifact, FPF **must** by default create a correctly formatted `CA-A` Analysis Report Carrier **in** the `02_analysis/` Folder of the narrowest resolved Scope Unit that **contains** the analyzed Claim Scope; routing-only work **must not** persist a report, an explicit non-persistent request **must** remain non-persistent, **and** unresolved identity, admission, topology, **or** placement **must** stop persistence rather than fall back **to** an ad hoc report Folder.
