---
identity:
  atom_id: AN-S-1760
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: active
  version: 29
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Serialize External Project Goal References

## Claim

### Prose Claim


references to Current and historical external Project Goal Atoms.


**every** Reference **to** a Current external Project Goal Atom **must** use its canonical Current Atom ID, not its current Carrier filename stem.

A Reference **to** an Archived external Project Goal Atom **must** use its canonical Atom ID qualified once with its unchanged numeric Version when historical identity is required. A Current Project Goal reference **must not** omit the canonical ID or fall back to a filename stem; this Delivery creates no ID-less Current exception.
