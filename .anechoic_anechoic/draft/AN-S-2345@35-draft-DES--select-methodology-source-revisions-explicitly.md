---
identity:
  atom_id: AN-S-2345
context:
  container:
    component: C00
  tier: 2
  lens: DES
state:
  status: draft
  version: 35
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Select Methodology Source revisions explicitly

## Claim scope

Methodology Source updates or downgrades applied by a Project.

## Claim

a Project **must** apply a Methodology Source update **or** downgrade **only** by selecting an identified source revision **and** reconciling affected Project authority; the selection **must not** silently rewrite other Methodology Sources **or** Project-owned Atoms.
