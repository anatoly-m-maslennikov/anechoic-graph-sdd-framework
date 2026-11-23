---
atom_family: SPEC
atom_id: AN-S-40
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 29
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Append governed action records independently of real-change commits

# Append governed action records independently of real-change commits

APPEND_CHANGE_RECORDS **must** append supplied actual governed-action observations independently of that action's real-change Git commit.

## Append boundary

- append **may** occur **before** **or** **after** a real-change commit **and** **must not** be its admission gate.
- use plain Journal append/read under CA-R-1491, **without** prior-history, chain, validation, canonical-receipt, deduplication, retry **or** recovery prerequisites.
- preserve supplied observations **without** a Project-conformance judgment **or** fabricated baseline. a later Project change does **not** rebind an observation **to** later state.
- each requested append is an append, including repeated data. reading returns recorded entries **without** migrating, repairing **or** replaying them.

## Storage behavior

- reuse the shared Project Journal append/read implementation. do **not** introduce another writer, validator, reconciliation state **or** proof gate.
- leave existing entries unchanged; report actual I/O failure **and** any observed partial append truthfully, **without** automatic retry **or** source-effect replay.
- do **not** acquire a Git-effect lease, alter the index **or** create a Commit as part of append/read. a separately requested Journal-only Git commit remains governed by COMMIT_CHANGE_SET **and** its unchanged Git checks.
- Journal data records observations; it does **not** authorize **or** certify source changes, lifecycle outcomes, Run completion **or** Git effects.
