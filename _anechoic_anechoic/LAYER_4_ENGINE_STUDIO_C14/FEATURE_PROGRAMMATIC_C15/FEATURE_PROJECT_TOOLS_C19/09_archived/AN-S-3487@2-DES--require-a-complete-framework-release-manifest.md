---
atom_family: SPEC
atom_id: AN-S-3487
container:
  component: C19
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 16:08:43 +0400
---
## Summary

Require a complete Framework release manifest

# Summary

Require a complete Framework release manifest

## Scope

The candidate N+1 package inventory and derived outputs required for a Release Version promotion.

## Claim

The candidate manifest **must** inventory and digest the complete declared Framework package, including the selected Framework Methodology source delivery, its accepted compiled runtime output, required Engine components, the project-local `ca` Skill payload, and the candidate image inputs; an Engine-Tools-only inventory is not a complete release manifest.

## Details

Every listed carrier has one repository-relative path, byte digest, role, and destination binding. The manifest SHA-256 is the content-addressed candidate release identity. Source authority remains a source input, while runtime and image copies are derived outputs; a manifest does not make an unreviewed layout, image, or installation current.
