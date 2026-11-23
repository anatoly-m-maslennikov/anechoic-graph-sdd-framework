---
atom_family: TKT
atom_id: AN-T-1907
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: 2026-11-10 06:56:53 +0400
---

## Summary

Review and fix Engine Roles and Scope placement

## Objective

Check actual Claims against current Role definitions and the latest Operator corrections. Find internal technical material incorrectly classified as a Requirement; check outcome Requirements independently of their Subject branch. Review owning Scope Units, promotion/demotion and permissions. Prepare role changes with replacement lineage and connected-reference plans.

## Subtasks

Each subtask is a batch of at most 15–20 minutes. Repeat per Scope Unit; give each subagent one Scope Unit.

- [ ] Review pass one on a same-Scope batch.
- [ ] Fix findings and prepare or refine the affected Drafts.
- [ ] Run independent pass two on the corrected batch.
- [ ] Fix pass-two findings and recheck affected earlier criteria.
- [ ] Record a small Work Report and thin coverage entries.

## Definition of Done

Role and Scope decisions are evidenced, source permissions are checked, and any broader/narrower move or role replacement has a reviewed Draft and impact record. Tasks track work; specification changes belong in RMEDO. No runtime implementation is performed here.

## Reviewed inputs

P2870 is Done. Use the 494-source snapshot, corrected Claim Drafts, the latest Operator decisions and the independent review packets. Missing identity is not a semantic-review hold. Treat carrier-encoded lower_snake named values as valid under D657; do not title-case them merely to work around a reader bug. Keep native-plugin extraction D707 deferred.
