---
atom_family: SPEC
atom_id: AN-S-1647
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 31
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Use external Analysis Atoms as review envelopes

## Claim scope

external reviews, their imported External Analysis Report Atoms, and the internal Analyses derived from them.

## Claim

an external review **must** be imported as an External Analysis Report Atom whose governed envelope identifies its source, provenance, reviewed scope, original body, **and** native attachments **without** requiring a provider-specific finding schema. one internal Analysis derives from that Atom, records the project's finding-level interpretation **and** dispositions, **and** becomes the **only** Analysis source from which project-owned Concern, Plan, Requirement, Method, Evaluation, **or** Delivery Atoms are derived. **every** accepted disposition that changes project meaning **or** work is materialized **in** its owning ANECHOIC Content Role; rejected **or** non-actionable findings remain **only** **in** the internal Analysis.
