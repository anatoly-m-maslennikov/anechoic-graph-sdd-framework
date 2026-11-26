---
atom_family: SPEC
atom_id: AN-S-438
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "active"
  version: 31
  updated_at: "2026-11-25T20:14:07.781591+00:00"
---
## Summary

Require Portable-Safe Carrier Addresses

## Claim

### Prose Claim


Project-owned Carrier address segments.


**every** Project-owned Carrier address segment

- **must** use **only** portable automation-safe ASCII letters, digits, underscores, hyphens, **and** dots, with `@` admitted in the Archive and Draft identity markers defined by AN-S-3160,
- **must not** contain whitespace, control characters, path separators, shell metacharacters, empty **or** reserved segments, **or** unsafe leading **or** trailing characters,
- **and** **must** remain sibling-unique under ASCII case folding.
