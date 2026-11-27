---
atom_family: TKT
atom_id: AN-T-4036
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T01:30:46.657003+00:00"
---
## Summary

Provide pinned Project Spec rows after DuckDB ingestion

## Acceptance

Expose an admitted Project snapshot through the existing database owner. Preserve source identity, Header, body, and original carrier digest. Give consumers an explicit outcome while the snapshot is unavailable.

## Evidence

C71 stages and reads a single snapshot under its returned ID. The Worker
checks that ID, preserves the exact source rows, and refuses an unavailable
or mismatched response. The compiler receipt rejects a different ID.
See `an-t-3476-asset-and-snapshot.xml` and the independent receipt check
`astra-postfix-snapshot-receipt.log` in the session evidence.
