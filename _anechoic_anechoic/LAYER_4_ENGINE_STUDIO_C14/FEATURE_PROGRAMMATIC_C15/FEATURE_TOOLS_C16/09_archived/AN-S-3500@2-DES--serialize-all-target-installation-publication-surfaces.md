---
atom_family: SPEC
atom_id: AN-S-3500
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Serialize all target installation publication surfaces

# Summary

Serialize all target installation publication surfaces

## Scope

the mutual exclusion boundary for target runtime effects.

## Claim

the INSTALL_TOOLS facade **must** use the same per-Project lock for selector, wrappers, Skill, projection and state publication, and **must not** let a competing installation publish any subset.

## Details

The lock names target context, owner run, operation, command digest and lock generation; every publication reopens it and revalidates inputs. The lock is project-specific, so separate selected Projects do not serialize each other. Candidate construction and image proof cannot bypass it.
