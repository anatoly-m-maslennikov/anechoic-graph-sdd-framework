---
atom_family: SPEC
atom_id: AN-S-4246
container:
  component: C45
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 20:32:03 +0400
---

## Summary

Deliver hourly Workbench query-log files

## Claim

### Prose Claim

Deliver the raw technical query log as direct UTF-8 NDJSON appends under `.anechoic_runtime/workbench/query_log`. An actual Run appends one record to its UTC-hour file, named `query-log-YYYY-MM-DD-HH.ndjson`. Check does not append a record. There is no buffer, staging file, backfill, retry, queue, row cap or additional event field.

Every new and returned retained record has exactly these seven fields: `log_id`, `at`, `sql`, `outcome`, `error`, `row_count` and `column_count`. Preserve the existing outcome semantics and exact approved SQL. A failed Run has null counts when unavailable. Never store result rows, result schema, View state, source data or a query result table in this log.

On append, list and get, retain and return only records whose UTC `at` is less than 48 hours old. Apply that two-day query-log lifetime independently of result retention and independently of the watcher change log, which has distinct ownership and semantics. Saved Views and their Journal records have no query-log TTL.

Read the legacy `.anechoic_runtime/workbench/query-log.json` single-file list as compatibility input alongside retained hourly records. Its retained records remain readable until the same 48-hour expiry. Do not rewrite, migrate, backfill or stage legacy bytes. New records never append to that file. A log write failure follows the existing stderr/response warning boundary and does not discard a completed Run result.
