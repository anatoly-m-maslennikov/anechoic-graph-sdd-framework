---
atom_family: TKT
atom_id: AN-T-1919
container:
  atom: AN-T-1940
priority: 2
context:
  template: task
state:
  status: archived
  version: 3
  updated_at: 2026-11-10 21:20:58 +0400
---

## Summary

Rebuild review and fix the Engine main-subject graph

## Objective

After the full review/fix cycle and source adoption, rebuild the scoped main-subject graph from the actual adopted Current sources. Review the graph against those sources and the latest Operator decisions. Fix findings, then rebuild and recheck until the graph passes. Do not start the implementation Epic before this gate and the current Epic are complete.

## Subtasks

- [ ] Review the adopted source selection and confirm obsolete sources are archived. (ETA: up to 15–20 min.)
- [ ] Rebuild the main-subject graph and record its exact source selection. (ETA: up to 15–20 min.)
- [ ] Independently review the graph for missing, extra, stale, duplicate or wrongly placed topics and references. (ETA: up to 15–20 min.)
- [ ] Fix findings in the affected source Drafts and repeat the affected review/adoption checks. (Repeat same-Scope batches, each up to 15–20 min.)
- [ ] Rebuild and independently check again after the fixes. (ETA: up to 15–20 min.)
- [ ] Record a small Work Report with the passing graph and remaining explicit exclusions.

## Definition of Done

The main-subject graph matches the adopted Current sources in scope, obsolete sources are excluded from current authority, and review findings are fixed and rechecked. Any later accepted source change repeats the affected review/adoption and graph checks before the implementation handoff. Unrelated scopes, existing Archives, benchmark fixtures and deferred plugin/old-Tool work remain preserved.
