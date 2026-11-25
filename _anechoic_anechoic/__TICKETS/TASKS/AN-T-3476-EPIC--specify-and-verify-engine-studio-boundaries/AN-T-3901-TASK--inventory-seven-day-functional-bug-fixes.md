---
atom_family: TKT
atom_id: AN-T-3901
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 2
  updated_at: '2026-11-24T11:50:30.612932+00:00'
---
## Summary

Inventory the seven-day functional bug fixes

## Work

Inspect tickets, Git history, and the worktree for the Operator's window 2026-11-17T15:38:02+04:00 through 2026-11-24T15:38:02+04:00. Identify confirmed functional bug fixes and distinguish candidates, non-functional changes, duplicates, and uncertain cases. Record source coverage and limits.

For each confirmed fix, record the behavior, evidence, affected paths, exact historical buggy revision, fixed revision or worktree state, and relevant regression evidence. Identify cases where an exact revision or fixed state cannot be established.

The Operator excluded current runtime review. Inventory already found and fixed bugs and preserve historical provenance.

## Acceptance

The inventory accounts for the scoped sources and gives evidence and revision identifiers for each confirmed functional fix. Candidates and unsupported or uncertain cases remain explicit and available for follow-up.

## Progress

`$BB_THREAD_STORAGE/seven-day-commit-coverage.json` records 30 commits reachable from HEAD whose titles begin with `fix` in the exact rolling window. This is a candidate filter, not a confirmed bug total.

Nine candidates are incorporated in the golden corpus. One additional CRLF fix is corroborated in checkpoint `b5f7ed5266`. Two candidates remain partial: `15a1f8e142` has a recording observer only; `8a51f94e30` uses an injected error and historical reachability is not established. The remaining titled commits are unevaluated.

Keep this Task open for uncovered candidates and ticket and checkpoint provenance. Do not review current runtime.
