---
atom_family: SPEC
atom_id: AN-S-278
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-09-09 23:10:38 +0400
---
## Summary

Keep operator settings out of the Scope Unit Graph generator

# Keep operator settings out of the Scope Unit Graph generator

## Test case

change **`=1`** initialization value **in** the authoritative Project Settings Artifact **and** **`=1`** Authority Mode selection **in** Framework Instance Settings, while leaving Project Atoms unchanged. rebuild the Project Scope Unit Graph Projections.

## Acceptance criteria

the generator uses the appropriate Settings revision for **every** exposed value **without** a Project-specific effective-value catalog **or** an Atom-owned current settings selection. output bindings identify the changed Settings Artifacts; the generator **and** the Projection **must not** become their authority.
