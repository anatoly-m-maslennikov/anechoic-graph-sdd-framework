---
atom_family: TKT
atom_id: AN-T-2094
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-10 03:36:34 +0400
---

## Summary

Verify content extraction for admitted Engine carriers

## Objective

Implement and test the adopted content-reader corrections using valid Current/Draft carrier examples, including Engine M514/M515 and the newly reviewed source layouts. Keep source authoring conventions separate from reader bugs. Gather applicable Method Policies and the exact adopted RMEDO before changing code.

## Subtasks

- [ ] Review the admitted reader specification and source examples. (ETA: up to 15 min.)
- [ ] Verify grouped and legacy-compatible Headers and admitted named Role/Form spellings. (ETA: up to 15 min.)
- [ ] Implement the smallest common reader correction and real-interface Evaluation. Split before 20 minutes.
- [ ] Verify declared Claim/Operation extraction without exposing undeclared content. (ETA: up to 15 min.)
- [ ] Record results and remaining coverage limits. (ETA: up to 15 min.)

## Definition of Done

Valid admitted sources expose their declared content through query_run. Invalid sources and undeclared folders retain their governed handling. Existing fixtures and a real-project canary cover the correction. No mass Atom rewrite substitutes for a reader fix.
