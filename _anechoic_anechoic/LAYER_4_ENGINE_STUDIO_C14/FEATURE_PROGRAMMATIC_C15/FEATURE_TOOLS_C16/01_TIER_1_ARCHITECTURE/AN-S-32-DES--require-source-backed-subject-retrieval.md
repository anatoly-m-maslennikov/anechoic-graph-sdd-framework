---
atom_family: SPEC
atom_id: AN-S-32
concern:
  subject: "Carrier"
  path: "Model"
  relation: "is_contained_by"
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 18
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Require Source-Backed Subject Retrieval

# Require Source-Backed Subject Retrieval

the Applicable Methodology Retrieval Tool **must** return **only** generated projected current RMEDO Atom Carriers that match the exact Subject **or** Process query through `subjects.governs` **or** enter its transitive prerequisite closure through `subjects.depends_on`, preserve compilation order, **and** resolve **every** returned Carrier **to** its exact authoritative Source Carrier.
