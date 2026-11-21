---
atom_family: TKT
atom_id: AN-T-1916
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: done
  version: 3
  updated_at: 2026-11-10 21:28:00 +0400
---

## Summary

Create the follow-up Engine implementation Epic

## Objective

Create the separate implementation Epic from accepted Code Synopsis dispositions. Reconcile existing P2791 work and source references to avoid duplicate implementation tasks. Record concrete work, dependencies and acceptance checks without embedding specification in tasks. Do not implement or release.

## Subtasks

Each subtask is a batch of at most 15–20 minutes. Repeat per Scope Unit; give each subagent one Scope Unit.

- [x] Check the next same-Scope evidence batch and fix its inputs.
- [x] Review pass one using actual sources and prepare the scoped dispositions.
- [x] Fix pass-one findings.
- [x] Run independent pass two on the corrected evidence and handoff.
- [x] Fix pass-two findings and recheck affected earlier criteria.
- [x] Record a small Work Report and the exact handoff.

## Definition of Done

A separate implementation Epic accounts for accepted code changes and existing queued work, while this Epic remains a source-refinement result. Tasks track work; specification changes belong in RMEDO. No runtime implementation is performed here.

Implementation starts only after the current Epic is complete, including full source review/fix, promotion, obsolete-source archival and the passing main-subject graph check. Reconcile the implementation Epic prerequisites accordingly.

## Result

Reconciled P2791 and its existing tasks instead of creating a duplicate Epic. Removed stale blanket holds and contradictory prior entry claims, preserved known defects, release relocation and audit work, and added the Current map/graph handoff. P2791 stays Backlog and no runtime implementation started. P2903 records the handoff.
