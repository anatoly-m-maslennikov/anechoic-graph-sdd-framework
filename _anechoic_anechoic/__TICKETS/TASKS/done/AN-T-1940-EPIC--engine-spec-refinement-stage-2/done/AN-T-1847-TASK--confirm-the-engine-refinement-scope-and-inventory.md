---
atom_family: TKT
atom_id: AN-T-1847
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: done
  version: 4
  updated_at: 2026-11-09 07:59:08 +0400
---

## Summary

Confirm the Engine refinement scope and inventory

## Objective

Establish the complete Current MED inventory and the related R, O and I reading set before refining the specification.

## Working procedure

Follow the parent Epic working procedure. Each item below is repeated in same-Scope batches of up to 15 minutes; decompose a larger batch before starting.

## Subtasks

- [x] Resolve the Engine tree and Workbench capability ownership through query_run; mark each included or excluded Scope Unit. (ETA: up to 15 min per batch.)
- [x] Inventory Current MED by Scope Unit and source ID@Version; identify related Requirements, Operations, policies and Code Synopses without making them another migration corpus. (ETA: up to 15 min per batch.)
- [x] Record exclusions, held unreadable sources and missing inputs in the thin inventory; review and fix its coverage. (ETA: up to 15 min per batch.)

## Definition of Done

Every Current MED candidate has one inclusion, exclusion or held disposition. ENGINE-local and all eligible descendant sources are counted; Workbench tools are included regardless of owner. No hidden deferral is counted as reviewed.
