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
  status: "done"
  version: 3
  updated_at: "2026-11-27T03:24:55.370415+00:00"
---
## Summary

Inventory the seven-day functional bug fixes

## Work

Inspect tickets, Git history, and the worktree for the Operator's window 2026-11-17T15:38:02+04:00 through 2026-11-24T15:38:02+04:00. Identify confirmed functional bug fixes and distinguish candidates, non-functional changes, duplicates, and uncertain cases. Record source coverage and limits.

For each confirmed fix, record the behavior, evidence, affected paths, exact historical buggy revision, fixed revision or worktree state, and relevant regression evidence. Identify cases where an exact revision or fixed state cannot be established.

The Operator excluded current runtime review. Inventory already found and fixed bugs and preserve historical provenance.

## Acceptance

The inventory accounts for the scoped sources and gives evidence and revision identifiers for each confirmed functional fix. Candidates and unsupported or uncertain cases remain explicit and available for follow-up.

## Inventory results

The historical inventory screens 257 non-merge commits in the scoped
window. It classifies the 30 titled fixes by Git diff. It screens 227
other commits by subject and changed paths and inspects the 27 stronger
candidates. One combined activation checkpoint remains unattributed.

The evidence identifies 24 existing case-specific Git replays and
three additional pairs with verified archive digests. The native
Manifest timestamp case adds an exact old and fixed Python replay.
The Lean check for that case records its observations. It does not
prove the historical compiler's semantics.

The report preserves the exact source paths, parents, and revisions.
It records candidate fixes, combined checkpoints, and archive pairs
whose Git revisions are unavailable. No current runtime was reviewed.

The consolidated receipt is `an-t-3901-inventory-final.json` in the
session evidence. It links the full Git screen and the replay index.
