---
identity:
  atom_id: AN-S-1945
context:
  container:
    component: C43
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T01:42:12.539601+00:00'
---

## Summary

Expose declared carrier conflicts

## Claim

### Prose Claim

For every readable selected Atom, including loaded Archives, compare its declared `file.name` and `file.path` with the other declared properties that identify its carrier. Derive expected values only from the existing canonical declared carrier rules. Expose each conflict as one query-visible audit row with the Atom identity, source path, issue category `declared_carrier_inconsistency`, observed and expected or related values, and the diagnostic location when available. If no applicable canonical rule exists, report `missing_carrier_rule` instead of guessing a filename grammar. Do not infer a replacement value, change the source file, or emit a row when no conflict exists.

