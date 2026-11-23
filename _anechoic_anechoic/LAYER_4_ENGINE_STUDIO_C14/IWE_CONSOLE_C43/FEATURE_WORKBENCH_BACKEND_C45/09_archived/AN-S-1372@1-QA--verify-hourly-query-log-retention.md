---
atom_family: SPEC
atom_id: AN-S-1372
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 20:32:03 +0400
---

## Summary

Verify hourly query-log retention

## Claim

### Prose Claim

Using the real backend query log, verify these cases:

| Case | Expected result |
| --- | --- |
| UTC rollover | Runs on adjacent UTC hours append one NDJSON line to their respective `query-log-YYYY-MM-DD-HH.ndjson` files. |
| Record shape | Every new/listed/fetched retained record has exactly `log_id`, `at`, `sql`, `outcome`, `error`, `row_count` and `column_count`; no result row, schema or new event field is present. |
| Two-day boundary | A record younger than 48 hours remains listable/gettable; one at or beyond 48 hours is absent after append, list or get retention processing. |
| Legacy compatibility | Retained records in legacy `query-log.json` are listable/gettable with hourly records, while its exact bytes remain unchanged and no new record is appended, migrated or backfilled there. |
| Run boundary | Successful and failed Runs append once with the existing exact SQL/outcome/count semantics; Check appends none. A query-log write failure reports through the existing warning boundary without discarding a completed Run. |
| Separate lifetimes | Expiring query-log records neither changes saved Views/Journal records nor reads, writes or reclassifies watcher change-log or result-cache data. |

Exercise `query_log_list` and `query_log_get` through the real backend and MCP boundary across the UTC rollover and legacy compatibility cases. Do not accept a JSON-array rewrite, a seven-day retention result, a mocked filesystem, or a test that omits exact legacy-byte preservation as evidence.
