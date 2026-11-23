---
atom_family: SPEC
atom_id: AN-S-1761
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 16
  updated_at: 2026-10-20 21:17:20 +0400
---
## Summary

Serialize Assigned Atom Identities

# Summary

Serialize Assigned Atom Identities

## Scope

assigned Atom IDs.

## Claim

**every** assigned Current or Archived Atom ID **must** begin with the registered uppercase Project identity prefix. the canonical Project-owned Atom ID encoding **must** match `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>-<GLOBAL_NUMBER_WITHIN_CONTENT_ROLE>`. For a Draft, `atom_id` **may** be omitted or use a Draft-only marker: `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>-draft` for a new Atom, `<canonical-ID>@<proposed-version>-draft` for a new version of an existing Atom, or the compatible `<canonical-ID>@draft` form. These markers are permitted on a carried Draft source, not a Current source. Exact archived predecessor bytes remain governed by actual-history preservation and are not normalized by this rule. The role-only new-Atom marker allocates no canonical number. the Atom Content Role Identity Letter **must** be **in** (Concern: C, Analysis: A, Plan: P, Requirement: R, Method: M, Evaluation: E, Delivery: D, Implementation: I, Operations: O). a `<PROJECT_PREFIX>-P` Identifier **must** identify a Plan Atom, including one labeled Epic, **and** **must not** identify a separate non-Atom collection.

## Details
