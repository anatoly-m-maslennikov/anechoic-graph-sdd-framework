---
atom_family: SPEC
atom_id: AN-S-438
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 22
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Require Portable-Safe Carrier Addresses

# Summary

Require Portable-Safe Carrier Addresses

## Scope

Project-owned Carrier address segments.

## Claim

**every** Project-owned Carrier address segment

- **must** use **only** portable automation-safe ASCII letters, digits, underscores, hyphens, **and** dots, with `@` admitted **only** **in** the `@<version>` Archive suffix immediately **before** the file extension, as specified by CA-D-289,
- **must not** contain whitespace, control characters, path separators, shell metacharacters, empty **or** reserved segments, **or** unsafe leading **or** trailing characters,
- **and** **must** remain sibling-unique under ASCII case folding.

## Details
