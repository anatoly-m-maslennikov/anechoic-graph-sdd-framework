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
  version: 26
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Serialize Assigned Atom Identities

## Claim scope

assigned Atom IDs.

## Claim

**every** assigned Current or Archived Atom ID **must** begin with the registered uppercase Project identity prefix. the canonical Project-owned Atom ID encoding **must** match `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>-<GLOBAL_NUMBER_WITHIN_CONTENT_ROLE>`. Every Draft Atom **must** carry a Draft-only `atom_id` marker: `<canonical-ID>@<proposed-version>-draft` for a proposed revision of an existing Atom, or `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>-draft` for a new Atom; `@<proposed-version>-draft` occurs once in the ID and matching Draft filename identity segment. A Draft marker is permitted on a Draft source, not a Current source. The role-only new-Atom marker allocates no canonical number. For Archived predecessors, qualify the Atom-ID filename segment and `atom_id` as `<canonical-ID>@<old-version>` exactly once, preserving its numeric Version and Updated At; do not require an exact-byte archive carrier. the Atom Content Role Identity Letter **must** be **in** (Concern: C, Analysis: A, Plan: P, Requirement: R, Method: M, Evaluation: E, Delivery: D, Operations: O). a `<PROJECT_PREFIX>-P` Identifier **must** identify a Plan Atom, including one labeled Epic, **and** **must not** identify a separate non-Atom collection.
