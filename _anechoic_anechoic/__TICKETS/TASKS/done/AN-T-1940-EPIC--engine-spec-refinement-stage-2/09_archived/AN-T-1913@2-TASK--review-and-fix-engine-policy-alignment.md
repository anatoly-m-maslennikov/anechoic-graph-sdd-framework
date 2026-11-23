---
atom_family: TKT
atom_id: AN-T-1913
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: 2026-11-10 13:10:49 +0400
---

## Summary

Review and fix Engine policy alignment

## Objective

Review each source against applicable local and inherited MED policies and related sources. Check surviving policies and Solutions before adding another Atom. Resolve authority conflicts through the approved Operator process; do not let implementation behavior silently redefine the specification.

## Subtasks

Each subtask is a batch of at most 15–20 minutes. Repeat per Scope Unit; give each subagent one Scope Unit.

- [ ] Review pass one on a same-Scope batch.
- [ ] Fix findings and prepare or refine the affected Drafts.
- [ ] Run independent pass two on the corrected batch.
- [ ] Fix pass-two findings and recheck affected earlier criteria.
- [ ] Record a small Work Report and thin coverage entries.

## Definition of Done

Applicable policies and related MED are recorded; contradictions have accepted corrections or explicit Questions, with independent work continuing. Tasks track work; specification changes belong in RMEDO. No runtime implementation is performed here.

## Reviewed inputs

P2876 is Done for relation semantics and canonical endpoints. Use fresh candidates, Current defaults/Form definitions and actual receiving Scope Delegations. Confirm exact local Role/Form and main-subject permissions; add only needed finite permissions with Current or explicitly candidate-only attestations. This does not alias old/new roots or move the Scope tree. Retiring trials need dispositions rather than new permissions. Scope/Tier edge ordering remains P2878. Recheck each changed delegation and its affected receiver sources independently.
