---
atom_family: SPEC
atom_id: AN-S-1494
structure:
  container:
    component: C9
  tier: 2
context:
  lens: DES
state:
  status: draft
  version: 30
  updated_at: 2026-11-11 18:12:55 +0400
---
## Summary
Govern Requirement conflicts by tier

## Claim

### Prose Claim


ANECHOIC **must** resolve conflicts among active Requirements other than Requirements expressing Project-wide foundational invariants through explicit rules determined by their applicability tiers rather than presentation order, Concern priority, **or** implicit interpretation.

## Details

Draft review: Before promotion, reconcile the role of tier with CA-R-2149: numeric tier alone does not select a conflict winner. Retain the Operator's decision authority.
