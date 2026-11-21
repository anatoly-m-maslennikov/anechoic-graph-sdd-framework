---
atom_family: SPEC
atom_id: AN-S-3188
structure:
  container:
    component: C61
  tier: 2
context:
  lens: SWD
relations:
  REFERENCES:
  - AN-S-3187@1-draft
  - AN-S-3159@2
  - AN-T-2921
state:
  status: draft
  version: 1
  updated_at: '2026-11-21T16:47:20.457433+00:00'
---

## Summary

Check local state and named channel grants

## Claim

### Prose Claim

- Resolve the owner of the accessed state. Follow aliases to that owner.
- `pure` permits immutable constants and explicit inputs and returns. Reject mutable module state, writes to global or nonlocal state, and ambient access.
- `local` is the default. Permit private mutation within its Component or Package boundary. Reject exporting mutable state or accessing another unit's private state.
- A charter adds named channels with `r`, `w`, or `rw` grants to `local`. Reject unlisted channels and access outside the listed mode.
- Report the file, line, owner or channel, and read or write for each finding. Use unresolved when the source, target, ownership, or access cannot be established.
