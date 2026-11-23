---
atom_family: SPEC
atom_id: AN-S-3747
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 23
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Separate candidate Project Structure from active authority

## Claim scope

the transition of a staged Project Structure candidate to active authority.

## Claim

a staged Project Structure candidate **must** use the filename `project_structure.candidate.toml` inside the explicitly selected migration workspace, outside the canonical active path. no ordinary consumer **may** discover it as active authority; candidate validation requires an explicit candidate path. cutover **must** install the validated candidate at the canonical path **only** **after** freshness, authorization, reference repairs, consumer readiness **and** recoverability checks pass. the old active bytes **must** remain recoverable through accepted change evidence **without** becoming another active structural source. the candidate **must** be retired **after** successful activation **or** rejection; failure **must not** leave two files eligible for normal authority resolution.
