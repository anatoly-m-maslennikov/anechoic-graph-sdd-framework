---
identity:
  atom_id: AN-T-1858
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

Review and fix MED tiers

## Objective

Make numeric Tiers consistent with the refined specification and its declared relations.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [x] Pass one: check tiers, relation directions, scope ancestry and admitted cross-scope permissions against the active model and latest Operator decisions. (ETA: up to 15 min per batch.)
- [x] Fix supported tier assignments after claim, Form and relation corrections; preserve valid Tier-0 Scope Contracts and admitted exceptions. (ETA: up to 15 min per batch.)
- [x] Pass two: recheck the affected graph and fix remaining ordering conflicts without inventing policy meaning from a Tier label. (ETA: up to 15 min per batch.)

## Definition of Done

Every changed Tier has a model-backed reason. Numeric ordering, Scope Contract rules and admitted exceptions hold; Tier numbers do not decide Policy versus Decision.
