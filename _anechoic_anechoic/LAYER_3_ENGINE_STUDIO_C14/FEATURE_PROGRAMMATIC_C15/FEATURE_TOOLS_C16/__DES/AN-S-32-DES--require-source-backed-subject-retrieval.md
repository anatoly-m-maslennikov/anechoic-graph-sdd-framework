---
atom_family: SPEC
atom_id: AN-S-32
structure:
  container:
    component: C16
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 17
  updated_at: 2026-10-27 19:59:52 +0400
---
## Summary

Require Source-Backed Subject Retrieval

# Require Source-Backed Subject Retrieval

the Applicable Methodology Retrieval Tool **must** return **only** generated projected current RMEDO Atom Carriers that match the exact Subject **or** Process query through `subjects.governs` **or** enter its transitive prerequisite closure through `subjects.depends_on`, preserve compilation order, **and** resolve **every** returned Carrier **to** its exact authoritative Source Carrier.
