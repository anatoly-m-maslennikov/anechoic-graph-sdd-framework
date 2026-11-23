---
atom_family: TKT
atom_id: AN-T-1863
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-11-09 05:40:47 +0400
---

## Summary

Review and fix Claim versus Role mismatches

## Objective

Make each selected Atom’s Role match what its actual Claim contributes.

## Working procedure

Follow the parent Epic working procedure. Work in same-Scope batches of up to 15 minutes and keep a small Work Report.

## Subtasks

- [ ] Pass one: read the full actual Claim and relevant Semantics and Details; compare the meaning with the current Role declarations, independently of topic, Form, filename and existing code. (ETA: up to 15 min per batch.)
- [ ] Prepare corrections for supported R/M/E/D/O mismatches and mixed-Role claims. Apply the active identity and replacement rules for a Role change; do not silently relabel a Current Atom. (ETA: up to 15 min per batch.)
- [ ] Pass two: review the corrected Drafts, including splits and affected relations; record uncertain bounded choices as C/Question and continue independent work. (ETA: up to 15 min per batch.)

## Definition of Done

Every selected MED source has a Claim-versus-Role disposition. Role mismatches with R or O are explicitly resolved or held; a broader inherited topic or architectural term alone does not determine Role.
