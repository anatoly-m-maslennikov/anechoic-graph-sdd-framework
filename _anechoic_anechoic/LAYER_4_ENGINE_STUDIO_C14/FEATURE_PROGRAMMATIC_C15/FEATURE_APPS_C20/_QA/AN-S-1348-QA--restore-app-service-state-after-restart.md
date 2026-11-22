---
atom_family: SPEC
atom_id: AN-S-1348
container:
  component: C20
tier: 2
context:
  lens: QA
state:
  status: active
  version: 18
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Restore App service state after restart

## Claim

### Prose Claim

#### Claim checked

the App service restores owned lifecycle state **without** treating derived **or**
transient interface state as project authority.

#### Test case

Provide governed source, a derived database snapshot, one running background
task, **and** transient interface state; terminate **and** restart the local App
service.

#### Acceptance criteria

Governed source remains authoritative, rebuildable derived state is
reconciled, unfinished background work follows its declared recovery rule, **and**
transient interface state is neither mistaken for project authority nor
silently persisted.

#### Failure disposition

Reject service recovery **when** authority changes, derived state remains stale,
work is lost **or** duplicated, **or** transient state is silently promoted **to** durable
state.

#### Sources

- [Python documentation: task groups](https://docs.python.org/3/library/asyncio-task.html#task-groups)
- [Python documentation: SQLite transaction control](https://docs.python.org/3/library/sqlite3.html#transaction-control)
