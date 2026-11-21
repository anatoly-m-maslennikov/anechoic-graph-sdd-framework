---
atom_family: SPEC
atom_id: AN-S-1372
container:
  component: C45
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 8
  updated_at: '2026-11-14T01:09:05.032209+00:00'
---
## Summary

Verify hourly query-log retention

## Claim

### Prose Claim

Verify hourly files, record fields, 48-hour retention, legacy reads, and
background writer behavior through the real Workbench backend and MCP.

## Details

### Hourly files and record shape

Verify adjacent UTC hours append NDJSON to their respective
`query-log-YYYY-MM-DD-HH.ndjson` files.

Every retained record has exactly `log_id`, `at`, `sql`, `outcome`, `error`
, `row_count`, and `column_count`.

### Retention and legacy compatibility

Records younger than 48 hours remain listable and gettable. Those at or beyond
48 hours disappear during append, list, and get retention.

Legacy `query-log.json` remains byte-identical and listable and gettable beside
hourly records. No new record is appended, migrated, or backfilled there. Verify
backend/MCP rollover and legacy cases.

### Background writes

Successful and failed Run each submit once to an ordered background writer after
synchronous Save; Check submits none. Run returns without waiting.

### Failure and shutdown boundaries

Writer failure reports stderr without retry or warning and preserves the
completed result. Expiry does not alter saved Views or Journal, watcher log, or
result cache.

Orderly shutdown drains submitted history. A crash may lose unflushed history
but not sources or saved items.
