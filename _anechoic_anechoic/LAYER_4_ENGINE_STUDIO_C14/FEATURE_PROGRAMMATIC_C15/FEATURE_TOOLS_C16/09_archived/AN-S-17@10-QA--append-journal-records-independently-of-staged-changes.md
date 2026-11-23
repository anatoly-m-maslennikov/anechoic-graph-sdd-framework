---
atom_family: SPEC
atom_id: AN-S-17
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 06:27:03 +0400
---
## Summary

Append Journal records independently of staged changes

# Append Journal records independently of staged changes

## Claim checked

APPEND_CHANGE_RECORDS appends **and** reads supplied actual observations independently of unrelated staged Git changes, **without** mutating the index **or** authorizing a Git effect.

## Test case

1. supply an actual change observation, retain existing Journal entries **and** stage an unrelated repository File.
2. request plain append, **then** read the stored entries. do **not** invoke COMMIT_CHANGE_SET **or** a Journal-only commit.
3. explicitly append the same supplied data again; separately read existing historical entries **without** migration.

## Acceptance criteria

- each requested append retains its supplied observation; the second explicit append is **not** suppressed as a duplicate. no prior-history, chain, digest, canonical-receipt, retry **or** recovery condition is required.
- existing Journal entries remain unchanged **and** readable as recorded. no synthetic baseline, prior event **or** source-state reconstruction is created.
- the complete Git index **and** unrelated File bytes remain unchanged. append/read does **not** stage, unstage, acquire a Git-effect lease **or** create a Commit.
- retain truthful I/O failure **and** actual partial observations **without** automatic retry **or** source-effect replay. an append result is **not** proof **or** permission for a source **or** Git effect.

## Failure disposition

reject an implementation that gates append/read on staged changes **or** previous records, modifies prior Journal entries **or** the Git index, changes supplied observations, introduces deduplication/retry/validation machinery **or** presents the log as effect permission **or** proof.
