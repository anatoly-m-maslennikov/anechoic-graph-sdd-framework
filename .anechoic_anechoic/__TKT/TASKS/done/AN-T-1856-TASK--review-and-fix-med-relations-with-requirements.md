---
identity:
  atom_id: AN-T-1856
context:
  container:
    atom: AN-T-1940
  tier: 4
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-11-09 07:59:08 +0400
---

## Summary

Review and fix MED relations with Requirements

## Objective

Make the relations between Requirements and MED express their actual contribution.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [x] Pass one: inspect actual active relation declarations and trace each selected MED contribution to its Requirements and related MED. (ETA: up to 15 min per batch.)
- [x] Fix missing, misleading or obsolete direct links and supported replacement links in Drafts; derive inverse links from the declarations. (ETA: up to 15 min per batch.)
- [x] Pass two: recheck both endpoints, semantics, specialization and connected consumers without changing unrelated Requirements or Operations. (ETA: up to 15 min per batch.)

## Definition of Done

Declared method-for, evaluation-for, delivery-for and other applicable relations have correct endpoints and meaning. Canonical direct names come from active declarations, not guessed aliases.
