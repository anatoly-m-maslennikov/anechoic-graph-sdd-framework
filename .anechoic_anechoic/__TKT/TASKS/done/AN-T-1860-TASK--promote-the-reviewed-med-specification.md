---
identity:
  atom_id: AN-T-1860
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

Promote the reviewed MED specification

## Objective

Adopt only the reviewed specification changes and verify their real source state.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [x] Review the exact adoption batch, source versions, permissions and replacement bindings before promotion. (ETA: up to 15 min per batch.)
- [x] Promote or replace only accepted Drafts under the current lifecycle model, using the declared replacement relation; preserve existing Archived sources. (ETA: up to 15 min per batch.)
- [x] Query the actual Current sources, rebuild relevant topic/relation views through available supported paths, and fix adoption discrepancies. (ETA: up to 15 min per batch.)

## Definition of Done

Every admitted source is promoted, replaced, retained or explicitly held. Current source readback matches the reviewed result; Drafting, adoption and implementation are reported separately.
