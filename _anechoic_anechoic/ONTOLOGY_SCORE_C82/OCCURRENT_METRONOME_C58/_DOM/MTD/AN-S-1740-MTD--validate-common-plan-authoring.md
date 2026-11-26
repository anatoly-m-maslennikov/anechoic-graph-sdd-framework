---
atom_family: SPEC
atom_id: AN-S-1740
container:
  component: C58
tier: 4
context:
  lens: DOM/MTD
state:
  status: active
  version: 31
  updated_at: '2026-11-25T21:19:16.984293+00:00'
---
## Summary

Validate common Plan authoring

## Claim

Check a planning Ticket against its declared Template and AN-S-3160. Require its authored Markdown carrier. Check the intended work, the planned decomposition, or both. A Ticket with neither has no established outcome.

Check that the Definition of Done identifies observable evidence under AN-S-2306. Check terminal descendant outcomes under AN-S-1604. A navigation Label leaves these checks applicable.

Report each failed check with the Ticket ID, observed content, and governing rule.
