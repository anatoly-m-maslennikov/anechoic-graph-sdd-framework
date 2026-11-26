---
atom_family: SPEC
atom_id: AN-S-3563
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 21
  updated_at: 2026-10-20 21:17:02 +0400
---
## Summary

Serialize Draft Atom Filenames with an Empty Number

# Summary
Serialize Draft Atom Filenames with an Empty Number

## Scope
Project-owned Draft Atom filenames.

## Claim

**every** Project-owned Draft Atom filename **must** begin with `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>` **before** its mutable components. When `atom_id` is omitted, use the existing empty-number form `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>--`. When a Draft Atom ID is carried, the filename **must** carry that exact Draft-only marker in the identity segment before the mutable components, as specified by CA-D-378.

## Details

### Draft Atom Identity

Draft filenames follow the optional marker forms under CA-D-378 and CA-D-446; when `atom_id` is carried, the filename remains aligned with that exact Draft marker.
