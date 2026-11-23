---
atom_family: SPEC
atom_id: AN-S-4325
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:34:40 +0400
---

## Summary

Expose declared carrier conflicts

## Claim

### Prose Claim

For every readable selected Current or Draft Atom, compare its declared `file.name` and `file.path` with the other declared properties that identify its carrier. Derive expected values only from the existing canonical declared carrier rules. Expose each conflict as one query-visible audit row with the Atom identity, source path, issue category `declared_carrier_inconsistency`, observed and expected or related values, and the diagnostic location when available. If no applicable canonical rule exists, report `missing_carrier_rule` instead of guessing a filename grammar. Do not infer a replacement value, change the source file, or emit a row when no conflict exists.

