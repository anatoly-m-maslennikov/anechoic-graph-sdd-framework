---
identity:
  atom_id: AN-S-1372
context:
  container:
    component: C45
  tier: 5
  lens: QA
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T20:51:17.423875+00:00'
---
## Summary

Verify hourly query-log retention

## Claim

### Prose Claim

Use the real backend to verify that adjacent UTC hours append NDJSON to their respective `query-log-YYYY-MM-DD-HH.ndjson` files. Each retained record has exactly `log_id`, `at`, `sql`, `outcome`, `error`, `row_count` and `column_count`. Records younger than 48 hours remain listable and gettable. Records at or beyond 48 hours disappear during append, list or get retention.

Legacy `query-log.json` remains byte-identical and listable and gettable beside hourly records. No record is appended, migrated or backfilled there. Successful or failed Run submits once to an ordered background writer after synchronous Save. Check submits none, and Run returns without waiting. Writer failure reports stderr without retry or warning and preserves the completed result.

Expiry does not alter saved Views or Journal, watcher log or result cache. Verify backend and MCP rollover and legacy cases. Orderly shutdown drains submitted history. A crash may lose unflushed history but not sources or saved items.
