---
atom_family: TKT
atom_id: AN-T-2087
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-11-11 00:44:41 +0400
---

## Summary

Relocate release implementation and tests

## Objective

Review and implement the adopted FRAMEWORK_DELIVERY specification for the complete local/public release families. Relocate their implementation and tests, update affected callers and verify the resulting release entry points. Keep generic Engine dependencies with their existing responsibilities.

## Subtasks

- [ ] Review the next implementation batch against Current RMEDO and applicable Method Policies. (ETA: up to 15 min.)
- [ ] Prepare and review the bounded relocation and caller changes. (ETA: up to 20 min per batch.)
- [ ] Apply each reviewed batch and run its relevant checks. (ETA: up to 20 min per batch.)
- [ ] Verify both release entry points and report remaining limitations. (ETA: up to 20 min.)

## Definition of Done

The affected implementation, tests, callers and delivery references agree with the adopted specification. Local/public release behavior and safety checks remain covered. Real publication or release requires its own authorized Run; this Task does not itself authorize either.
