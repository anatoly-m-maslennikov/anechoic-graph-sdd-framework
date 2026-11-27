---
atom_family: SPEC
atom_id: AN-S-4740
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: active
  version: 2
  updated_at: '2026-11-27T11:11:44.727957+00:00'

---

## Summary

Check source ownership and boundaries

## Claim

### Prose Claim

Static checks Manifest import and export boundaries across Engine Studio.
Require Lean for state analysis. Fail when Lean is missing or execution
fails, and report unresolved state cases separately.

#### Ownership and boundaries

Check source ownership and imports against the declared code boundaries.
Check declared state boundaries and Python child import boundaries. Check
Python launchers for bytecode containment and the independent launch roots
required by AN-S-3310. Apply AN-S-1342 to temporary and cache placement.
