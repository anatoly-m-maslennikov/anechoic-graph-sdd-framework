---
atom_family: TKT
atom_id: AN-T-1861
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 05:38:07 +0400
---

## Summary

Revise Code Synopses against the refined specification

## Objective

Identify what the actual implementation should contribute to RMEDO and what should be fixed in code.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [ ] Review existing I / Code Synopsis reports against actual code locations and state; do not treat historical Draft reports as Current authority. (ETA: up to 15 min per batch.)
- [ ] Revise or create bounded Code Synopsis Drafts and compare actual behavior with the adopted specification; map relevant Atom IDs@Versions to implemented modules. (ETA: up to 15 min per batch.)
- [ ] Review and fix each disposition: adopt into RMEDO, fix code, already aligned, or defer with a reason; draft supported RMEDO corrections and recheck them. (ETA: up to 15 min per batch.)

## Definition of Done

Every confirmed mismatch has code evidence and an explicit specification-or-code disposition. Code is not automatically adopted as intended behavior. No implementation changes are made.
