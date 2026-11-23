---
atom_family: SPEC
atom_id: AN-S-3746
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Bind Project Structure revisions **to** source evidence

# Summary

Bind Project Structure revisions **to** source evidence

## Scope

Project Structure Revision bindings.

## Claim

a Project Structure Revision binding **must** identify the exact authoritative TOML bytes by SHA-256 Digest **and** the completed change event **in** the canonical Event Log under applicable Journal authority. the binding **must** distinguish the selected pre-change state, resulting state, **and** actual completion **or** failure; missing **or** conflicting event evidence leaves provenance currentness unknown. the TOML Carrier **must not** duplicate Atom Revision fields **or** store its own self-referential digest. a consumer **may** parse **and** validate the selected bytes **without** claiming completed change provenance **when** that provenance is unresolved.

## Details
