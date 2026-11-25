---
atom_family: SPEC
atom_id: AN-S-2791
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 9
  updated_at: "2026-11-25T22:46:57.718917+00:00"
---

## Summary

Separate Property names and values

## Claim

### Prose Claim

- The complete path identifies a Property. Sibling names are unique on each
  bearer.
- Occurrence bounds govern presence. Value formats and bounds apply to the
  direct values of each occurrence. See CA-R-2327 for count semantics.
- Resolve local and inherited Declarations before checking dependent Properties.
  Only declared dependents are admitted. An applicable name selector admits
  the names and counts it declares.
- In a Subject selector, each `.*` selects one level and `.**` selects all
  descendant levels. Apply chained selectors from left to right.

