---
atom_family: SPEC
atom_id: AN-S-2303
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T20:43:05.748213+00:00"
---
## Summary

Validate Atom prose and exact references

## Claim

### Prose Claim

Evaluate authored Atom prose against the applicable ASD-STE100-aligned profile. Check exact canonical Terms, Scope Unit Names, registered references, and literal identifiers against their authoritative sources.

Use fixtures with ordinary sentence and list starts, correct exact names and references in both positions, altered exact names or references, mismatched Term meanings, and literal Python, SQL, Topic, and Relation tokens that must remain unchanged. Identify the exact profile and authority revisions and expected results.

Report each affected occurrence, its observed and expected form, and the authority. Treat ambiguous or unavailable evidence as unresolved. Record a Concern and do not rewrite the source.
