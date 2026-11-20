---
identity:
  atom_id: AN-S-1509
context:
  container:
    component: C14
  tier: 3
  lens: SWD
state:
  status: active
  version: 17
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Diagnose, admit, and repair implementation failures

## Claim

### Prose Claim

**to** handle a failure, retain failing evidence, diagnose its category, admit retry only through current permission, confidence and retry guards, repair the admitted defect, and return for renewed preparation or checking.

## Details

### Scope

the diagnosed repair path after a selected Implementation Workflow check does not pass.

Changed failures, stale evidence, unavailable authority or non-progressing work block. Repair preserves issue evidence and does not create or promote an M atom.
