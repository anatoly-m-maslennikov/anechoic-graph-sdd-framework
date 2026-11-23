---
atom_family: TKT
atom_id: AN-T-2115
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: 2026-11-11 06:21:04 +0400
---

## Summary

Implement the new Atom Lifecycle Tools

## Objective

Implement the admitted Atom Lifecycle Workflows as new Tools using the existing adapters. Use Current RMEDO as the specification; review any required Drafts before adoption or implementation.

## Subtasks

- [ ] Review the Atom Lifecycle Workflow and adapter contracts. Fix gaps in RMEDO before implementation. (ETA: up to 15 min.)
- [ ] Gather the applicable Method Policies and scoped implementation inputs. (ETA: up to 15 min.)
- [ ] Implement and register the new Tools using the existing adapters. Split into batches of up to 20 min.
- [ ] Verify the admitted lifecycle operations through the real Tool interface using a disposable Project. Split checks into batches of up to 20 min.
- [ ] Review and fix the result; record a short Work Report. (ETA: up to 15 min.)

## Definition of Done

The admitted Atom Lifecycle Workflows are available as new Tools, use the existing adapters, and pass their real-interface Evaluations. Retired Tools and the generic Workflow engine stay deferred.


## Contract review

C730 records the adoption and corrected-input decision for Tool publication. Current O127/O128/O129, R1432/R1788, and E521 supply the exact-target Direct Update effect and its readback criteria. Review the selected carriers and retained adapter primitives before implementation.
