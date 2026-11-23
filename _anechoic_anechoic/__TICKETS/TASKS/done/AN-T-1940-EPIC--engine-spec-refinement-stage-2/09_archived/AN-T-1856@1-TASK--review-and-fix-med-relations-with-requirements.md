---
atom_family: TKT
atom_id: AN-T-1856
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

Review and fix MED relations with Requirements

## Objective

Make the relations between Requirements and MED express their actual contribution.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [ ] Pass one: inspect actual active relation declarations and trace each selected MED contribution to its Requirements and related MED. (ETA: up to 15 min per batch.)
- [ ] Fix missing, misleading or obsolete direct links and supported replacement links in Drafts; derive inverse links from the declarations. (ETA: up to 15 min per batch.)
- [ ] Pass two: recheck both endpoints, semantics, specialization and connected consumers without changing unrelated Requirements or Operations. (ETA: up to 15 min per batch.)

## Definition of Done

Declared method-for, evaluation-for, delivery-for and other applicable relations have correct endpoints and meaning. Canonical direct names come from active declarations, not guessed aliases.
