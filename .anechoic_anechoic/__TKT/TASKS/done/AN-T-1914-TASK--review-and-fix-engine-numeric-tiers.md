---
identity:
  atom_id: AN-T-1914
context:
  container:
    atom: AN-T-1940
  tier: 4
  template: task
state:
  status: done
  version: 2
  updated_at: 2026-11-10 19:14:23 +0400
---

## Summary

Review and fix Engine numeric Tiers

## Objective

Review numeric Tiers and applicable graph-ordering rules after relation and Scope corrections. Recheck changed endpoints, ancestry and admitted exceptions. Preserve the distinction between a Tier number and its optional label.

## Subtasks

Each subtask is a batch of at most 15–20 minutes. Repeat per Scope Unit; give each subagent one Scope Unit.

- [x] Review pass one on a same-Scope batch.
- [x] Fix findings and prepare or refine the affected Drafts.
- [x] Run independent pass two on the corrected batch.
- [x] Fix pass-two findings and recheck affected earlier criteria.
- [x] Record a small Work Report and thin coverage entries.

## Definition of Done

Every changed governing relation passes the current Tier/Scope rules or has an explicit unresolved disposition; no named tier is substituted for numeric data. Tasks track work; specification changes belong in RMEDO. No runtime implementation is performed here.

## Final source checkpoint

Numeric ordering now passes for 364 selected candidate Atoms and 373 governing links. Every candidate has a declared owner and numeric Tier; all selected governing targets follow the same-Scope lower-Tier rule or permitted ancestor/explicit exception, with no cycle. Actual Header pins are recorded in candidate-ordering-validation.json. Recheck after any endpoint, owner, Tier or relation edit and again after adoption.
