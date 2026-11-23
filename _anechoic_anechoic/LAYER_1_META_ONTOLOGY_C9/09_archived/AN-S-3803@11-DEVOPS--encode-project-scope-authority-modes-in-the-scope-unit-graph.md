---
atom_family: SPEC
atom_id: AN-S-3803
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-19 15:55:42 +0400
---
## Summary

Encode project scope authority modes in the Scope Unit Graph

# Summary

Encode project scope authority modes in the Scope Unit Graph

## Scope

the `authority_mode` of a retained Project Scope Unit Graph Projection.

## Claim

**if** a Project Scope Unit Graph Projection is retained for compatibility, its `authority_mode` **must** be a derived effective value: an explicit unit override from Project Structure, **otherwise** the applicable Framework Instance Settings selection. it **must not** select **or** own that mode, become a required input **to** a direct Project Structure consumer, **or** require creation of a separate structural Projection.

## Details
