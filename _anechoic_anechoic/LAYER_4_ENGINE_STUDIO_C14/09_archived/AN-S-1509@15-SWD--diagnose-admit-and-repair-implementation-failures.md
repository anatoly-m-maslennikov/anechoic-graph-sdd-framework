---
atom_family: SPEC
atom_id: AN-S-1509
container:
  component: C14
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 15
  updated_at: 2026-11-09 14:41:40 +0400
---

## Summary

Diagnose, admit, and repair implementation failures

## Claim

### Prose Claim

**to** handle a failure, retain the actual failing evidence, diagnose its category, admit retry only through current permission/confidence/retry guards, repair the admitted defect, and return for renewed preparation or checking.

## Details

### Scope

the diagnosed repair path after a selected Implementation Workflow check does not pass.

Changed failures, stale evidence, unavailable authority, or non-progressing work block. Repair preserves issue evidence and does not create or promote an M atom.
