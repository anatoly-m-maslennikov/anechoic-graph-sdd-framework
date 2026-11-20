---
identity:
  atom_id: AN-S-1372
context:
  container:
    component: C45
  tier: 5
  lens: QA
state:
  status: active
  version: 6
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify hourly query-log retention

## Claim

### Prose Claim

Use the real backend to verify adjacent UTC hours append NDJSON to their respective `query-log-YYYY-MM-DD-HH.ndjson` files; every retained record has exactly `log_id`, `at`, `sql`, `outcome`, `error`, `row_count`, `column_count`. Records younger than 48 hours remain listable/gettable; those at or beyond 48 hours disappear during append/list/get retention.

Legacy `query-log.json` remains byte-identical and listable/gettable beside hourly records; no new record is appended, migrated or backfilled there. Successful/failed Run submits once to an ordered background writer after synchronous Save; Check submits none and Run returns without waiting. Writer failure reports stderr without retry/warning and preserves completed result. Expiry does not alter saved Views/Journal, watcher log or result cache. Verify backend/MCP rollover and legacy cases; orderly shutdown drains submitted history, while crash may lose unflushed history but not sources/saved items.
