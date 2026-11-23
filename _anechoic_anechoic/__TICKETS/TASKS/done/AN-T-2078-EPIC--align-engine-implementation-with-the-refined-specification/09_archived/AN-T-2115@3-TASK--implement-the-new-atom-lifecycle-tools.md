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
  version: 3
  updated_at: 2026-11-11 13:25:55 +0400
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

The Operator selected the six separate Atom Lifecycle Workflow Drafts. Use Update for Scope Unit changes. Review and adopt the Workflow, Step and Action definitions before implementing the Tools. CA-C-730 tracks remaining contract and publication checks.
