---
atom_family: SPEC
atom_id: AN-S-4261
container:
  component: C45
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Write query history in the background

## Claim

### Prose Claim

Use one ordered background writer in each Workbench owner for automatic query history. Submit one record after each Run and any requested synchronous Save handling, using the submission timestamp. Do not wait for its file write before returning the Run result. Serialize query-log reads and writes so readers never see a partial line. Report background failures to stderr, without retry or a response warning. Drain submitted writes on orderly owner shutdown; a process crash may lose unflushed history.

Explicit query and View saves still finish writing before returning their IDs. Keep the query log separate from watcher event delivery, watcher history, result retention and saved Journal records.
